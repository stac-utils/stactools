from collections import defaultdict
import re
from typing import Dict

from pystac.extensions.eo import Band

from stactools.aster.constants import ASTER_FILE_NAME_REGEX, ASTER_BANDS
from stactools.core.projection import epsg_from_utm_zone_number


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
        return 'AST_L1T_{}_{}'.format(self.start_datetime,
                                      self.production_datetime)

    @property
    def file_prefix(self):
        return 'AST_L1T_{}_{}_{}'.format(self.start_datetime,
                                         self.production_datetime,
                                         self.processing_number)

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

    return epsg_from_utm_zone_number(utm_zone_number, south)


def get_sensors_to_bands() -> Dict[str, Band]:
    sensor_to_bands = defaultdict(list)

    # Gather the bands for each sensor, sorted by band number
    for band in ASTER_BANDS:
        sensor_to_bands[band.name.split('_')[0]].append(band)
    for sensor in sensor_to_bands:
        sensor_to_bands[sensor] = sorted(
            sensor_to_bands[sensor],
            key=lambda b: re.search('([d]+)', b.name).group(1))

    return dict(sensor_to_bands)
