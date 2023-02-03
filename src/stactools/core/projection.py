import math
from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import pyproj
import rasterio.crs
import rasterio.transform

# Sinusoidal projection parameters found in Appendix B of
# https://modis-fire.umd.edu/files/MODIS_C6_BA_User_Guide_1.2.pdf
SINUSOIDAL_SPHERE_RADIUS = 6371007.181
SINUSOIDAL_TILE_METERS = 1111950
SINUSOIDAL_X_MIN = -20015109
SINUSOIDAL_Y_MAX = 10007555


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


def reproject_geom(
    src_crs: Union[pyproj.CRS, rasterio.crs.CRS, str],
    dest_crs: Union[pyproj.CRS, rasterio.crs.CRS, str],
    geom: Dict[str, Any],
    precision: Optional[int] = None,
) -> Dict[str, Any]:
    """Reprojects a geometry represented as GeoJSON from the src_crs to the dest
    crs.

    Args:
        src_crs (pyproj.crs.CRS, rasterio.crs.CRS, or str): Projection of input data.
        dest_crs (pyproj.crs.CRS, rasterio.crs.CRS, or str): Projection of output data.
        geom (dict): The GeoJSON geometry
        precision (int, optional): The precision of the reprojection operation.

    Returns:
        dict: The reprojected geometry
    """
    transformer = pyproj.Transformer.from_crs(src_crs, dest_crs, always_xy=True)
    result = deepcopy(geom)

    def fn(coords: Sequence[Any]) -> Sequence[Any]:
        coords = list(coords)
        for i in range(0, len(coords)):
            coord = coords[i]
            if isinstance(coord[0], Sequence):
                coords[i] = fn(coord)
            else:
                x, y = coord
                reprojected_coords = list(transformer.transform(x, y))
                if precision is not None:
                    reprojected_coords = [
                        round(n, precision) for n in reprojected_coords
                    ]
                coords[i] = reprojected_coords
        return coords

    result["coordinates"] = fn(result["coordinates"])

    return result


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


def sinusoidal_pixel_to_grid(
    pixel_coords: List[Tuple[float, float]],
    horizontal_tile: int,
    vertical_tile: int,
    tile_dimension: int,
) -> List[Tuple[float, float]]:
    """Transform MODIS and VIIRS sinusoidal projection pixel coordinates to
    grid coordinates.

    Args:
        pixel_coords (List[Tuple[float]]): List of pixel coordinate tuples in
            (column, row) order.
        horizontal_tile (int): Horizontal sinusoidal tile grid number.
        vertical_tile (int): Vertical sinusoidal tile grid number.
        tile_dimension (int): Tile pixel dimension. For example, MODIS 09A1
            product tiles are 2400x2400 pixels, so tile_dimension is 2400.

    Returns:
        List[Tuple[float]]: List of transformed sinusoidal projection grid
            coordinate tuples in (x, y) order.
    """
    pixel_width = SINUSOIDAL_TILE_METERS / tile_dimension
    grid_coords = []
    for column, row in pixel_coords:
        x = (
            column * pixel_width
            + horizontal_tile * SINUSOIDAL_TILE_METERS
            + SINUSOIDAL_X_MIN
        )
        y = (
            SINUSOIDAL_Y_MAX
            - row * pixel_width
            - vertical_tile * SINUSOIDAL_TILE_METERS
        )
        grid_coords.append((x, y))
    return grid_coords


def sinusoidal_grid_to_lonlat(
    grid_coords: List[Tuple[float, float]]
) -> List[Tuple[float, float]]:
    """Transform MODIS and VIIRS sinusoidal projection grid coordinates to
    spherical longitude and latitude.

    Args:
        grid_coords (List[Tuple[float]]): List of sinusoidal projection grid
            coordinate tuples in (x, y) order.

    Returns:
        List[Tuple[float]]: List of transformed spherical longitude and latitude
            coordinate tuples in (longitude, latitude) order.
    """
    lonlat = []
    for x, y in grid_coords:
        latitude = math.degrees(y / SINUSOIDAL_SPHERE_RADIUS)
        longitude = math.degrees(
            x / (SINUSOIDAL_SPHERE_RADIUS * math.cos(y / SINUSOIDAL_SPHERE_RADIUS))
        )
        lonlat.append((longitude, latitude))
    return lonlat
