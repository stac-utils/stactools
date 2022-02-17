from copy import deepcopy
from typing import Any, List, Optional, Union, Dict, Sequence

import pyproj
import rasterio.crs
import rasterio.transform


def epsg_from_utm_zone_number(utm_zone_number: int, south: bool) -> int:
    """Return the EPSG code for a UTM zone number.

    Args:
        utm_zone_number (int): The UTM zone number.
        south (bool): Whether this UTM zone is a south zone.

    Returns:
        int: The EPSG code number for the UTM zone.
    """
    crs = pyproj.CRS.from_dict({
        'proj': 'utm',
        'zone': utm_zone_number,
        'south': south
    })

    return int(crs.to_authority()[1])


def reproject_geom(src_crs: Union[pyproj.CRS, rasterio.crs.CRS, str],
                   dest_crs: Union[pyproj.CRS, rasterio.crs.CRS, str],
                   geom: Dict[str, Any],
                   precision: Optional[int] = None) -> Dict[str, Any]:
    """Reprojects a geometry represented as GeoJSON
    from the src_crs to the dest crs.

    Args:
        src_crs: pyproj.crs.CRS, rasterio.crs.CRS or str used to create one
            Projection of input data.
        dest_crs: pyproj.crs.CRS, rasterio.crs.CRS or str used to create one
            Projection of output data.
        geom (dict): The GeoJSON geometry
        precision

    Returns:
        dict: The reprojected geometry
    """
    transformer = pyproj.Transformer.from_crs(src_crs,
                                              dest_crs,
                                              always_xy=True)
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

    result['coordinates'] = fn(result['coordinates'])

    return result


def transform_from_bbox(bbox: List[float], shape: List[int]) -> List[float]:
    """Calculate the affine transformation (proj:transform)
    from the bbox (proj:bbox) and shape (proj:shape)

    Only take the first 6 elements, as that is all that is necessary.
    """
    return list(
        rasterio.transform.from_bounds(bbox[0], bbox[1], bbox[2], bbox[3],
                                       shape[1], shape[0]))[:6]
