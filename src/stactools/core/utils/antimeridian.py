"""`Antimeridian <https://en.wikipedia.org/wiki/180th_meridian>`_ utilities."""
import math
from enum import Enum, auto
from typing import Optional

import shapely.affinity
import shapely.geometry
import shapely.ops
from pystac import Item
from shapely.geometry import LineString, MultiPolygon, Polygon


class Strategy(Enum):
    """Strategy for handling antimeridian-crossing polygons."""

    SPLIT = auto()
    """Split the polygon into multiple polygons so none cross the
    antimeridian."""

    NORMALIZE = auto()
    """Keep the polygon as one polygon, but extend its values to be greater
    than 180 or less than -180."""


def fix_item(item: Item, strategy: Strategy) -> Item:
    """Modifies an item in-place to deal with antimeridian issues.

    If the item's geometry is not a :py:class:`Polygon`` or a
    :py:class:`MultiPolygon`, raises a :py:class:`ValueError`.

    Args:
        item (pystac.Item): The item to be modified.

    Returns:
        Item: The input item, whether it was modified or not.
    """
    geometry = shapely.geometry.shape(item.geometry)
    if isinstance(geometry, Polygon):
        multi_polygon = False
    elif isinstance(geometry, MultiPolygon):
        multi_polygon = True
    else:
        raise ValueError(
            "Can only fix antimeridian issues for Polygons or MultiPolygons, "
            f"geometry={geometry}"
        )
    if strategy == Strategy.NORMALIZE:
        if multi_polygon:
            normalized_geometry = normalize_multipolygon(geometry)
        else:
            normalized_geometry = normalize(geometry)
        if normalized_geometry:
            bbox = normalized_geometry.bounds
            item.geometry = shapely.geometry.mapping(normalized_geometry)
            item.bbox = bbox
    elif strategy == Strategy.SPLIT:
        if multi_polygon:
            split_geometry = split_multipolygon(geometry)
        else:
            split_geometry = split(geometry)
        if split_geometry:
            xmin = 180
            xmax = -180
            for geom in split_geometry.geoms:
                if geom.bounds[0] > xmax:
                    xmax = geom.bounds[0]
                if geom.bounds[2] < xmin:
                    xmin = geom.bounds[2]
            bounds = split_geometry.bounds
            # https://datatracker.ietf.org/doc/html/rfc7946#section-5.2
            item.bbox = [xmax, bounds[1], xmin, bounds[3]]
            item.geometry = shapely.geometry.mapping(split_geometry)
    return item


def split(polygon: Polygon) -> Optional[MultiPolygon]:
    """Splits a single WGS84 polygon into a multipolygon across the
    antimeridian.

    If the polygon does not cross the antimeridian, returns None. Only handles
    exterior rings (can't handle interior).

    Note:
        Will not work on polygons that enclose the north or south poles.

    Todo:
        Fix this

    Args:
        polygon (:py:class:`shapely.geometry.Polygon`): The input polygon.

    Returns:
        Optional[:py:class:`shapely.geometry.MultiPolygon`]:
            The output polygons, or None if no split occurred.
    """
    normalized = normalize(polygon)
    if normalized is None:
        return None
    if normalized.bounds[0] < -180:
        longitude = -180
    elif normalized.bounds[2] > 180:
        longitude = 180
    else:
        return None
    splitter = LineString(((longitude, -90), (longitude, 90)))
    split = shapely.ops.split(normalized, splitter)
    if len(split.geoms) < 2:
        return None
    geoms = list()
    for geom in split.geoms:
        geom = shapely.geometry.polygon.orient(geom)
        bounds = geom.bounds
        if bounds[0] < -180:
            geoms.append(shapely.affinity.translate(geom, xoff=360))
        elif bounds[2] > 180:
            geoms.append(shapely.affinity.translate(geom, xoff=-360))
        else:
            geoms.append(geom)
    return MultiPolygon(geoms)


def split_multipolygon(multi_polygon: MultiPolygon) -> Optional[MultiPolygon]:
    """Splits multiple WGS84 polygons into a multipolygon across the
    antimeridian.

    If none of the contained polygons cross the antimeridian, returns None. Only
    handles exterior rings (can't handle interior).

    Note:
        Will not work on polygons that enclose the north or south poles.

    Todo:
        Fix this

    Args:
        multi_polygon (:py:class:`shapely.geometry.MultiPolygon`): The input
            multi polygon.

    Returns:
        Optional[:py:class:`shapely.geometry.MultiPolygon`]:
            The output polygons, or None if no split occurred.
    """
    polygons = []
    for polygon in multi_polygon.geoms:
        split_polygon = split(polygon)
        if split_polygon:
            polygons.extend(split_polygon.geoms)
    if polygons:
        return MultiPolygon(polygons)
    else:
        return None


def normalize(polygon: Polygon) -> Optional[Polygon]:
    """'Normalizes' a WGS84 lat/lon polygon, or returns None if no changes were
    made.

    This converts the polygon's x coordinates to all be the same sign, even if
    the polygon crosses the antimeridian. E.g.:

    .. code-block:: python

        canonical = Polygon(((170, 40), (170, 50), (-170, 50), (-170, 40), (170, 40)))
        normalized = stactools.core.utils.antimeridian.normalize(canonical)
        assert normalized.equals(shapely.geometry.box(170, 40, 190, 50))

    Inspired by
    https://towardsdatascience.com/around-the-world-in-80-lines-crossing-the-antimeridian-with-python-and-shapely-c87c9b6e1513.

    Note:
        Will not work on polygons that enclose the north or south poles.

    Todo:
        Fix this

    Args:
        polygon (:py:class:`shapely.geometry.Polygon`): The input polygon.

    Returns:
        Optional[:py:class:`shapely.geometry.Polygon`]: The normalized polygon.
    """
    coords = list(polygon.exterior.coords)
    has_changes = False
    for index, (start, end) in enumerate(zip(coords, coords[1:])):
        delta = end[0] - start[0]
        if abs(delta) > 180:
            has_changes = True
            coords[index + 1] = (end[0] - math.copysign(360, delta), end[1])
    if not has_changes:
        return None
    polygon = shapely.geometry.polygon.orient(Polygon(coords))
    centroid = polygon.centroid
    if centroid.x > 180:
        return shapely.affinity.translate(polygon, xoff=-360)
    elif centroid.x < -180:
        return shapely.affinity.translate(polygon, xoff=+360)
    else:
        return polygon


def normalize_multipolygon(multi_polygon: MultiPolygon) -> Optional[MultiPolygon]:
    """'Normalizes' a WGS84 lat/lon multi polygon, or returns None if no
    changes were made.

    For each polygon in the multi-polygon, this converts the x coordinates to
    all be the same sign, even if the polygon crosses the antimeridian. Although
    the x coordinate sign within each polygon will be made the same, the sign
    may differ between polygons depending on their position relative to the
    antimeridian.

    Note:
        Will not work on polygons that enclose the north or south poles.

    Todo:
        Fix this

    Args:
        multi_polygon (:py:class:`shapely.geometry.MultiPolygon`): The input
            multi-polygon.

    Returns:
        Optional[:py:class:`shapely.geometry.MultiPolygon`]: The normalized
        multi-polygon.
    """
    polygons = list()
    changes_made = False
    for polygon in multi_polygon.geoms:
        normalized_polygon = normalize(polygon)
        if normalized_polygon:
            polygons.append(normalized_polygon)
            changes_made = True
        else:
            polygons.append(polygon)
    if changes_made:
        return MultiPolygon(polygons)
    else:
        return None
