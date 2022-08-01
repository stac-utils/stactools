import logging
from itertools import groupby
from typing import Any, Dict, Iterator, List, Optional, Tuple

import numpy
import numpy as np
import rasterio
import rasterio.features
from pystac import Item
from rasterio.crs import CRS
from rasterio.warp import transform_geom
from shapely.geometry import mapping, shape
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon

logger = logging.getLogger(__name__)

# Roughly 1 centimeter in geodetic coordinates
DEFAULT_PRECISION = 7


def update_geometry_from_asset_footprint(
    item: Item,
    *,
    asset_names: List[str] = [],
    precision: int = DEFAULT_PRECISION,
    densification_factor: Optional[int] = None,
    simplify_tolerance: Optional[float] = None,
    no_data: Optional[int] = None,
) -> bool:
    """
    Accepts an Item and an optional list of asset names within that item, and updates
    the geometry of that Item in-place with the data footprint derived from the first
    of the assets that exists in the Item.

    Two important operations during this calculation are the densification of the
    footprint in the native CRS and simplification of the footprint after reprojection.
    If the initial low-vertex polygon in the native CRS is not densified, this can result
    in a reprojected polygon that does not accurately represent the data footprint. For
    example, a MODIS asset represented by a rectangular 5 point Polygon in a sinusoidal
    projection will reproject to a parallelogram in EPSG 4326, when it would be more
    accurately represented by a polygon with two parallel sides and two curved sides.
    The difference between these representations is even greater the further away from
    the meridian and equator the asset is located.

    After reprojection to EPSG 4326, the footprint may have more points than desired.
    This can be simplified to a polygon with fewer points that maintain a minimum distance
    to the original geometry.

    Args:
        item (Item): The PySTAC Item to extend.
        asset_names (List[str]): The names of the assets for which to attempt to
            extract footprints. The first successful footprint will be used. If the
            list is empty, all assets will be tried until one is successful.
        precision (int): The number of decimal places to include in the coordinates for the
            reprojected geometry. Defaults to 3 decimal places.
        densification_factor (Optional[int]): The factor by which to increase point density within
            the polygon.
            A factor of 2 would double the density of points (placing one new point between each
            existing pair
            of points), a factor of 3 would place two points between each point, etc.
        simplify_tolerance (Optional[float]): All points in the simplified object will be within
            the tolerance distance of the original geometry, in degrees.
        no_data(Optional[int]): explicitly set the no data value if not in image metadata

    Returns:
        bool: True if the extent was successfully updated, False if not
    """
    asset_name_and_extent = next(
        data_footprints_for_data_assets(
            item,
            asset_names=asset_names,
            precision=precision,
            densification_factor=densification_factor,
            simplify_tolerance=simplify_tolerance,
            no_data=no_data,
        ),
        None,
    )
    if asset_name_and_extent is not None:
        _, extent = asset_name_and_extent
        item.geometry = extent
        return True
    else:
        return False


def data_footprints_for_data_assets(
    item: Item,
    *,
    asset_names: List[str] = [],
    precision: int = DEFAULT_PRECISION,
    densification_factor: Optional[int] = None,
    simplify_tolerance: Optional[float] = None,
    no_data: Optional[int] = None,
) -> Iterator[Tuple[str, Dict[str, Any]]]:
    """
    Accepts an Item and an optional list of asset names within that item, and
    produces an iterator over the same asset names (if they exist) and a
    dictionary representing a GeoJSON Polygon of the data footprint of the
    asset.  The data footprint is considered to be a convex hull around all
    areas within the raster that have data values (e.g., they do not have the
    "no data" value).

    See :py:meth:`update_geometry_from_asset_footprint` for more details about
    densification and simplification.

    Args:
        item (Item): The PySTAC Item to extend.
        asset_names (List[str]): The names of the assets for which to attempt to
            extract footprints. The first successful footprint will be used. If the
            list is empty, all assets will be tried until one is successful.
        precision (int): The number of decimal places to include in the coordinates for
            the reprojected geometry. Defaults to 3 decimal places.
        densification_factor (Optional[int]): The factor by which to increase point density
            within the polygon. A factor of 2 would double the density of points (placing one
            new point between each existing pair of points), a factor of 3 would place two points
            between each point, etc.
        simplify_tolerance (Optional[float]): All points in the simplified object will be within
            the tolerance distance of the original geometry, in degrees.
        no_data(Optional[int]): explicitly set the no data value if not in image metadata
    Returns:
        Iterator[Tuple[str, Dict[str, Any]]]: Iterator of the data extent as a geojson dict
            for each asset.
    """
    for name, asset in item.assets.items():
        if not asset_names or name in asset_names:
            href = asset.get_absolute_href()
            if href is None:
                logger.error(
                    f"Could not determine extent for asset '{name}', missing href"
                )
            else:
                extent = data_footprint(
                    href,
                    precision=precision,
                    densification_factor=densification_factor,
                    simplify_tolerance=simplify_tolerance,
                    no_data=no_data,
                )
                if extent:
                    yield name, extent
                else:
                    logger.error(f"Could not determine extent for asset '{name}'")


def _densify(
    point_list: List[Tuple[float, float]], densification_factor: int
) -> List[Tuple[float, float]]:
    """
        Densifies the number of points in a list of points by a factor. For example, a list of 5 points
        and a densification_factor of 2 will result in 10 points (one new point between each original
        adjacent points.

        Derived from code found at
        https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw  # noqa
     Args:
        point_list (List[Tuple[float, float]]): The list of points.
        densification_factor (int): The factor by which to densify the points. A larger densification factor
            should be used when reprojection causes in greater curvature from the original geometry.

    Returns:
        List[Tuple[float, float]]: a list of the densified points
    """
    points: Any = np.asarray(point_list)
    densified_number = len(points) * densification_factor
    existing_indices = np.arange(0, densified_number, densification_factor)
    interp_indices = np.arange(existing_indices[-1])
    interp_x = np.interp(interp_indices, existing_indices, points[:, 0])  # noqa
    interp_y = np.interp(interp_indices, existing_indices, points[:, 1])  # noqa
    densified_points = [(x, y) for x, y in zip(interp_x, interp_y)]
    return densified_points


def data_footprint(
    href: str,
    *,
    precision: int = DEFAULT_PRECISION,
    densification_factor: Optional[int] = None,
    simplify_tolerance: Optional[float] = None,
    no_data: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Produces a data footprint from the href of a raster file.

    See :py:meth:`update_geometry_from_asset_footprint` for more details about densification
    and simplification.

    Args:
        href (str): The href of the image to process.
        precision (int): The number of decimal places to include in the coordinates for the
            reprojected geometry. Defaults to 3 decimal places.
        densification_factor (Optional[int]): The factor by which to increase point density
            within the polygon. A factor of 2 would double the density of points (placing one
            new point between each existing pair of points), a factor of 3 would place two points
            between each point, etc.
        simplify_tolerance (Optional[float]): All points in the simplified object will be within
            the tolerance distance of the original geometry, in degrees.
        no_data(Optional[int]): explicitly set the no data value if not in image metadata. If
            set to None, this will return the footprint including no data values.

    Returns:
        List[Tuple[float, float]]: a list of the densified points
    """
    src = rasterio.open(href)

    # create datamask
    if no_data is None:
        no_data = src.nodata

    arr = src.read(1, out_shape=src.shape)
    data_val = 1 if no_data != 1 else 0

    if no_data is not None:
        arr[numpy.where(arr != no_data)] = data_val
    else:
        arr.fill(data_val)

    data_polygons = [
        shape(polygon_dict)
        for polygon_dict, region_value in rasterio.features.shapes(
            arr, transform=src.transform
        )
        if region_value == data_val
    ]

    if not data_polygons:
        return None
    elif len(data_polygons) == 1:
        polygon = data_polygons[0]
    else:
        polygon = MultiPolygon(data_polygons).convex_hull

    polygon = densify_reproject_simplify(
        polygon,
        src.crs,
        densification_factor=densification_factor,
        precision=precision,
        simplify_tolerance=simplify_tolerance,
    )

    return mapping(polygon)  # type: ignore


def densify_reproject_simplify(
    polygon: Polygon,
    crs: CRS,
    *,
    densification_factor: Optional[int] = None,
    precision: int = DEFAULT_PRECISION,
    simplify_tolerance: Optional[float] = None,
) -> Polygon:
    """
    From the input Polygon, densifies the polygon, reprojects it to EPSG:4326, and then
    simplifies the resulting polygon.

    See :py:meth:`update_geometry_from_asset_footprint` for more details about densification
    and simplification.

    Args:
        polygon (Polygon): The input Polygon
        crs (CRS): The CRS of the input Polygon
        densification_factor (Optional[int]): The factor by which to increase point density
            within the polygon. A factor of 2 would double the density of points (placing one
            new point between each existing pair of points), a factor of 3 would place two points
            between each point, etc.
        precision (int): The number of decimal places to include in the coordinates for the
            reprojected geometry. Defaults to 3 decimal places.
        simplify_tolerance (Optional[float]): All points in the simplified object will be within
            the tolerance distance of the original geometry, in degrees.

    Returns:
        Polygon: the reprojected Polygon
    """
    if densification_factor is not None:
        polygon = Polygon(_densify(polygon.exterior.coords, densification_factor))

    polygon = shape(transform_geom(crs, "EPSG:4326", polygon, precision=precision))

    if simplify_tolerance is not None:
        polygon = polygon.simplify(
            tolerance=simplify_tolerance, preserve_topology=False
        ).simplify(0)

    # simplify does not remove duplicate sequential points, so do that
    polygon = Polygon([k for k, _ in groupby(polygon.exterior.coords)])

    return polygon
