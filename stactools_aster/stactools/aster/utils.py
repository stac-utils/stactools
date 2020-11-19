from collections import abc
from copy import deepcopy
import re

import pyproj

from stactools.aster.constants import ASTER_FILE_NAME_REGEX


class AsterSceneId:
    def __init__(self, start_datetime, production_datetime, processing_number):
        self.start_datetime = start_datetime
        self.production_datetime = production_datetime
        self.processing_number = processing_number

    @property
    def item_id(self):
        """The ID used for STAC Items. Comprised of the start_datetime
        and production_datetime, which are sufficient for identifying
        the scene."""
        return '{}_{}'.format(self.start_datetime, self.production_datetime)

    @staticmethod
    def from_path(path):
        m = re.search(ASTER_FILE_NAME_REGEX, path)
        if m:
            start_datetime = m.group('start')
            production_datetime = m.group('production')
            processing_number = m.group('processing')
        else:
            raise Exception('File name does not match ASTER L1T 003 file name '
                            'pattern, which is needed to extract IDs.')

        return AsterSceneId(start_datetime, production_datetime,
                            processing_number)


def epsg_from_aster_utm_zone_number(utm_zone_number):
    south = False

    # ASTER LT1 uses negative numbers to indicate southern zones
    if utm_zone_number < 0:
        south = True
        utm_zone_number *= -1

    crs = pyproj.CRS.from_dict({
        'proj': 'utm',
        'zone': utm_zone_number,
        'south': south
    })

    return int(crs.to_authority()[1])


def reproject_geom(src_crs, dest_crs, geom):
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
