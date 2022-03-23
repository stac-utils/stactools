from enum import Enum, auto
import math
from typing import Optional

import shapely.affinity
import shapely.geometry
import shapely.ops
from pystac import Item
from shapely.geometry import Polygon, MultiPolygon, LineString


class Strategy(Enum):
    """Strategy for handling antimeridian-crossing polygons.

        - SPLIT: split the polygon at the antimeridian
        - NORMALIZE: keep the polygon as one, but extend it to > 180 or < -180.
    """
    SPLIT = auto()
    NORMALIZE = auto()


def fix_item(item: Item, strategy: Strategy) -> None:
    """Modifies an item in-place to deal with antimeridian issues.

    If the item's geometry is not a `Polygon`, raises a `ValueError`.

    Args:
        item (pystac.Item): The item to be modified.
    """
    geometry = shapely.geometry.shape(item.geometry)
    if not isinstance(geometry, Polygon):
        raise ValueError(
            f"Can only fix antimeridian issues for Polygons, geometry={geometry}"
        )
    if strategy == Strategy.NORMALIZE:
        normalized_geometry = normalize(geometry)
        if normalized_geometry:
            bbox = normalized_geometry.bounds
            item.geometry = shapely.geometry.mapping(normalized_geometry)
            item.bbox = bbox
    elif strategy == Strategy.SPLIT:
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


def split(polygon: Polygon) -> Optional[MultiPolygon]:
    """Splits a single WGS84 polygon into a multipolygon across the antimeridian.

    If the polygon does not cross the antimeridian, returns None. Only handles
    exterior rings (can't handle interior).

    NOTE: Will not work on polygons that enclose the north or south poles.
    TODO: Fix this

    Args:
        polygon (shapely.geometry.Polygon): The input polygon.

    Returns:
        Optional[shapely.geometry.MultiPolygon]: The output polygons, or None if
            no split occurred.
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
        bounds = geom.bounds
        if bounds[0] < -180:
            geoms.append(shapely.affinity.translate(geom, xoff=360))
        elif bounds[2] > 180:
            geoms.append(shapely.affinity.translate(geom, xoff=-360))
        else:
            geoms.append(geom)
    return MultiPolygon(geoms)


def normalize(polygon: Polygon) -> Optional[Polygon]:
    """'Normalizes' a WGS84 lat/lon polygon, or returns None if no changes were made.

    This converts the polygon's x coordinates to all be the same sign, even if
    the polygon crosses the antimeridian. E.g.:

    ```
    canonical = Polygon(((170, 40), (170, 50), (-170, 50), (-170, 40), (170, 40)))
    normalized = stactools.core.utils.antimeridian.normalize(canonical)
    assert normalized.equals(shapely.geometry.box(170, 40, 190, 50))
    ```

    Inspired by
    https://towardsdatascience.com/around-the-world-in-80-lines-crossing-the-antimeridian-with-python-and-shapely-c87c9b6e1513.

    NOTE: Will not work on polygons that enclose the north or south poles.
    TODO: Fix this

    Args:
        polygon (shapely.geometry.Polygon): The input polygon.

    Returns:
        Optional[shapely.geometry.Polygon]: The normalized polygon.
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
    polygon = Polygon(coords)
    centroid = polygon.centroid
    if centroid.x > 180:
        return shapely.affinity.translate(polygon, xoff=-360)
    elif centroid.x < -180:
        return shapely.affinity.translate(polygon, xoff=+360)
    else:
        return polygon
