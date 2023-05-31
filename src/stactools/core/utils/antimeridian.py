"""`Antimeridian <https://en.wikipedia.org/wiki/180th_meridian>`_ utilities.

Most of the functionality in this module is implemented in `antimeridian
<https://pypi.org/projects/antimeridian>`_.
"""

from __future__ import annotations

import math
import warnings
from enum import Enum, auto
from typing import Optional

import antimeridian
import shapely.affinity
import shapely.geometry
import shapely.ops
from pystac import Item
from shapely.geometry import MultiPolygon, Polygon


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
    if strategy == Strategy.NORMALIZE:
        if isinstance(geometry, Polygon):
            multi_polygon = False
        elif isinstance(geometry, MultiPolygon):
            multi_polygon = True
        else:
            raise ValueError(
                "Can only fix antimeridian issues for Polygons or MultiPolygons, "
                f"geometry={geometry}"
            )
        if multi_polygon:
            normalized_geometry = normalize_multipolygon(geometry)
        else:
            normalized_geometry = normalize(geometry)
        if normalized_geometry:
            bbox = list(normalized_geometry.bounds)
            item.geometry = shapely.geometry.mapping(normalized_geometry)
            item.bbox = bbox
    elif strategy == Strategy.SPLIT:
        fixed = antimeridian.fix_shape(geometry)
        item.bbox = antimeridian.bbox(fixed)
        item.geometry = fixed
    else:
        raise NotImplementedError(f"Unknown strategy: {strategy}")
    return item


def split(polygon: Polygon) -> Optional[MultiPolygon]:
    """Splits a single WGS84 polygon into a multipolygon across the
    antimeridian.

    .. deprecated:: v0.4.8
       Use the `antimeridian <https://pypi.org/project/antimeridan>`_ package
       instead.

    Args:
        polygon (:py:class:`shapely.geometry.Polygon`): The input polygon.

    Returns:
        Optional[:py:class:`shapely.geometry.MultiPolygon`]:
            The output polygons, or None if no split occurred.
    """
    warnings.warn(
        (
            "`stactools.core.utils.antimeridian.split` is deprecated. "
            "To fix polygons that cross the antimeridian, use the antimeridian "
            "package (https://pypi.org/project/antimeridian/)."
        ),
        DeprecationWarning,
    )
    fixed = antimeridian.fix_polygon(polygon)
    if fixed.geom_type == "MultiPolygon":
        return fixed
    else:
        return None


def split_multipolygon(multi_polygon: MultiPolygon) -> Optional[MultiPolygon]:
    """Splits multiple WGS84 polygons into a multipolygon across the
    antimeridian.

    .. deprecated:: v0.4.8
       Use the `antimeridian <https://pypi.org/project/antimeridan>`_ package
       instead.

    Args:
        multi_polygon (:py:class:`shapely.geometry.MultiPolygon`): The input
            multi polygon.

    Returns:
        Optional[:py:class:`shapely.geometry.MultiPolygon`]:
            The output polygons. Will not return None, but the Optional return
            type is kept to preserve backwards compatibility until this function
            is removed.
    """
    warnings.warn(
        (
            "`stactools.core.utils.antimeridian.split_multipolygon` is deprecated. "
            "To fix polygons that cross the antimeridian, use the antimeridian "
            "package (https://pypi.org/project/antimeridian/)."
        ),
        DeprecationWarning,
    )
    return antimeridian.fix_multi_polygon(multi_polygon)


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

    .. deprecated:: v0.4.8
        "Normalization" does not conform to the GeoJSON specification, and its
        use is discouraged.

    Args:
        polygon (:py:class:`shapely.geometry.Polygon`): The input polygon.

    Returns:
        Optional[:py:class:`shapely.geometry.Polygon`]: The normalized polygon.
    """
    warnings.warn(
        (
            "`stactools.core.utils.antimeridian.normalize` is deprecated. "
            "Normalization does not conform to the GeoJSON spec and its use is "
            "discouraged."
        ),
        DeprecationWarning,
    )
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

    .. deprecated:: v0.4.8
        "Normalization" does not conform to the GeoJSON specification, and its
        use is discouraged.

    Args:
        multi_polygon (:py:class:`shapely.geometry.MultiPolygon`): The input
            multi-polygon.

    Returns:
        Optional[:py:class:`shapely.geometry.MultiPolygon`]: The normalized
        multi-polygon.
    """
    warnings.warn(
        (
            "`stactools.core.utils.antimeridian.normalize_multipolygon` is deprecated. "
            "Normalization does not conform to the GeoJSON spec and its use is "
            "discouraged."
        ),
        DeprecationWarning,
    )
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


def enclose_poles(polygon: Polygon) -> Polygon:
    """Updates an anti-meridian-crossing polygon to enclose the poles.

    This works by detecting anti-meridian crossings and adding points to extend
    the geometry up to the north (or down to the south) pole. This is useful for
    (e.g.) polar-orbiting satellites who have swaths that go over the poles.

    .. deprecated:: v0.4.8
       Use the `antimeridian <https://pypi.org/project/antimeridan>`_ package
       instead.

    Args:
        polygon (:py:class:`shapely.geometry.Polygon`): An input polygon.

    Returns:
        :py:class:`shapely.geometry.Polygon`: The same polygon, modified to
        enclose the poles.

    Raises:
        ValueError: Raised if the polygon was split. This is to keep the return
        type the same until this function is removed.
    """
    warnings.warn(
        (
            "`stactools.core.utils.antimeridian.enclose_poles` is deprecated. "
            "To fix polygons that enclose the poles, use the antimeridian "
            "package (https://pypi.org/project/antimeridian/)."
        ),
        DeprecationWarning,
    )
    fixed = antimeridian.fix_polygon(polygon)
    if fixed.geom_type == "Polygon":
        return fixed
    else:
        raise ValueError("Input polygon was split and we cannot return a MultiPolygon")
