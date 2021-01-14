from collections import abc
from copy import deepcopy

import pyproj


def epsg_from_utm_zone_number(utm_zone_number, south):
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


def reproject_geom(src_crs, dest_crs, geom):
    """Reprojects a geometry represented as GeoJSON
    from the src_crs to the dest crs.

    Args:
        src_crs (str): String that can be passed into
            pyproj.Transformer.from_crs, e.g. "epsg:4326"
            representing the current CRS of the geometry.
        dest_crs (str): Similar to src_crs, representing the
            desired CRS of the returned geometry.
        geom (dict): The GeoJSON geometry

    Returns:
        dict: The reprojected geometry
    """
    transformer = pyproj.Transformer.from_crs(src_crs,
                                              dest_crs,
                                              always_xy=True)
    result = deepcopy(geom)

    def fn(coords):
        coords = list(coords)
        for i in range(0, len(coords)):
            coord = coords[i]
            if isinstance(coord[0], abc.Sequence):
                coords[i] = fn(coord)
            else:
                x, y = coord
                coords[i] = transformer.transform(x, y)
        return coords

    result['coordinates'] = fn(result['coordinates'])

    return result
