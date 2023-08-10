import json
import warnings
from typing import Any, Dict, List, Optional, Union, cast

import pyproj
import rasterio.crs
import rasterio.transform
from rasterio.warp import transform_geom
from shapely import Geometry
from shapely.constructive import remove_repeated_points
from shapely.geometry import mapping, shape

from .geometry import GeoInterface


def epsg_from_utm_zone_number(utm_zone_number: int, south: bool) -> int:
    """Returns the EPSG code for a UTM zone number.

    Args:
        utm_zone_number (int): The UTM zone number.
        south (bool): Whether this UTM zone is a south zone.

    Returns:
        int: The EPSG code number for the UTM zone.
    """
    crs = pyproj.CRS.from_dict({"proj": "utm", "zone": utm_zone_number, "south": south})

    return int(crs.to_authority()[1])


def reproject_shape(
    src_crs: rasterio.crs.CRS,
    dst_crs: rasterio.crs.CRS,
    geom: GeoInterface,
    precision: Optional[int] = None,
) -> Geometry:
    """Projects a shapely.Geometry and rounds the projected vertex coordinates
    to ``precision``.

    Duplicate points caused by rounding are removed.

    Args:
        src_crs (rasterio.crs.CRS): The CRS of the input geometry.
        dst_crs (rasterio.crs.CRS): The CRS of the output geometry.
        geom (GeoInterface): GeoJSON like dict or shapely geometry object to reproject
        precision (int): The number of decimal places to include in the final
            Geometry vertex coordinates.

    Returns:
        geom: the reprojected shapely geometry object
    """
    if precision is None:
        precision = -1  # rasterio uses -1 for "unspecified"
    return remove_repeated_points(
        shape(transform_geom(src_crs, dst_crs, geom, precision=precision))
    )


def reproject_geom(
    src_crs: Union[pyproj.CRS, rasterio.crs.CRS, str],
    dest_crs: Union[pyproj.CRS, rasterio.crs.CRS, str],
    geom: Dict[str, Any],
    precision: Optional[int] = None,
) -> Dict[str, Any]:
    """DEPRECATED.

    .. deprecated:: 0.5.0
        Use :func:`reproject_shape` instead.

    Reprojects a geometry represented as GeoJSON from the src_crs to the
    dest crs.

    Args:
        src_crs (pyproj.crs.CRS, rasterio.crs.CRS, or str): Projection of input data.
        dest_crs (pyproj.crs.CRS, rasterio.crs.CRS, or str): Projection of output data.
        geom (dict): The GeoJSON geometry
        precision (int, optional): The precision of the reprojection operation.

    Returns:
        dict: The reprojected geometry
    """
    warnings.warn(
        "``reproject_geom`` is deprecated and will be removed in v0.6.0. "
        "Use ``reproject_shape`` instead.",
        DeprecationWarning,
    )
    return cast(
        Dict[str, Any],
        json.loads(
            json.dumps(
                mapping(reproject_shape(src_crs, dest_crs, shape(geom), precision))
            )
        ),
    )


def transform_from_bbox(bbox: List[float], shape: List[int]) -> List[float]:
    """Calculate the affine transformation from the bbox and shape.

    Only take the first 6 elements, as that is all that is necessary.

    Args:
        bbox (list[float]): The bounding box of the transform.
        shape (list[int]): The shape of the transform.

    Returns:
        list[float]: The six-element GDAL transform.
    """
    return list(
        rasterio.transform.from_bounds(
            bbox[0], bbox[1], bbox[2], bbox[3], shape[1], shape[0]
        )
    )[:6]
