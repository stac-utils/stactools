from typing import List, Optional

import pystac
from pystac.utils import str_to_datetime

import rasterio
import rasterio.features
from rasterio import Affine as A
from rasterio.warp import transform_geom
from shapely.geometry import mapping, shape
import numpy as np
import os
import json
import logging

logger = logging.getLogger(__name__)


class RTCMetadata:
    def __init__(self, href):
        self.href = href

        def _load_metadata_from_asset(asset='local_incident_angle.tif', scale=1, precision=5):
            ''' key metadata stored in Geotiff tags '''
            with rasterio.Env(AWS_NO_SIGN_REQUEST='YES',
                              GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
                with rasterio.open(os.path.join(href, asset)) as src:
                    metadata = src.profile
                    metadata.update(src.tags())
                    # other useful things that aren't already keys in src.profile
                    metadata['PROJ_BBOX'] = list(src.bounds)
                    metadata['SHAPE'] = src.shape

                    bbox, footprint = _get_geometries(src, scale, precision)

            return metadata, bbox, footprint

        def _get_geometries(src, scale, precision):
            ''' scale can be 1,2,4,8,16. scale=1 creates most precise footprint
            at the expense of reading all pixel values. scale=2 reads 1/4 amount
            of data be overestimates footprint by at least 1pixel (20 meters).
            '''
            with rasterio.vrt.WarpedVRT(src, crs='EPSG:4326') as vrt:
                bbox = [np.round(x, decimals=precision) for x in vrt.bounds]

            arr = src.read(1, out_shape=(src.height // scale, src.width // scale))
            arr[np.where(arr != 0)] = 1
            transform = src.transform * A.scale(scale)

            for geom, val in rasterio.features.shapes(arr, transform=transform):
                if val == 1:
                    geometry = shape(
                        transform_geom(src.crs, "EPSG:4326", geom, precision=precision)
                        )
                    footprint = mapping(geometry.convex_hull)

                    return bbox, footprint

        def _get_provenance():
            ''' RTC products are from mosaiced GRD frames '''
            # NOTE: just GRD frame names? or additional info, like IPF from manifest.safe
            # <safe:software name="Sentinel-1 IPF" version="002.72"/>
            grd_ids = []
            for i in range(1, int(self.metadata['NUMBER_SCENES']) + 1):
                m = json.loads(self.metadata[f'SCENE_{i}_METADATA'])
                grd_ids.append(m['title'])

            return grd_ids

        def _get_times():
            ''' UTC start and end times of GRDs used in RTC product '''
            times = []
            for i in range(1, int(self.metadata['NUMBER_SCENES']) + 1):
                m = json.loads(self.metadata[f'SCENE_{i}_METADATA'])
                times += [m['start_time'], m['end_time']]
                start = str_to_datetime(min(times))
                end = str_to_datetime(max(times))
                mid = start + (end - start) / 2
            return start, mid, end

        self.metadata, self.bbox, self.geometry = _load_metadata_from_asset()
        self.grd_ids = _get_provenance()
        self.start_datetime, self.datetime, self.end_datetime = _get_times()

    @property
    def product_id(self) -> str:
        DATE = self.metadata['DATE'].replace('-', '')
        orbNames = {'ascending': 'ASC', 'descending': 'DSC'}
        ORB = orbNames[self.metadata['ORBIT_DIRECTION']]
        id = f"{self.metadata['MISSION_ID']}_{DATE}_{self.metadata['TILE_ID']}_{ORB}"
        return id

    @property
    def image_media_type(self) -> str:
        return pystac.MediaType.COG

    @property
    def shape(self) -> List[int]:
        return self.metadata['SHAPE']

    @property
    def image_paths(self) -> List[str]:
        return ['Gamma0_VV.tif', 'Gamma0_VH.tif', 'local_incident_angle.tif']

    @property
    def absolute_orbit(self) -> Optional[int]:
        return int(self.metadata['ABSOLUTE_ORBIT_NUMBER'])

    @property
    def relative_orbit(self) -> Optional[int]:
        '''https://forum.step.esa.int/t/sentinel-1-relative-orbit-from-filename/7042 '''
        adjust = {'S1B': 27, 'S1A': 73}
        rel_orbit = (
            (self.absolute_orbit - adjust[self.metadata['MISSION_ID']]) %
            175) + 1
        return rel_orbit

    @property
    def orbit_state(self) -> Optional[str]:
        return self.metadata['ORBIT_DIRECTION']

    @property
    def platform(self) -> Optional[str]:
        platformMap = dict(S1A='sentinel-1a', S1B='sentinel-1b')
        return platformMap[self.metadata['MISSION_ID']]

    @property
    def proj_bbox(self) -> Optional[str]:
        return self.metadata['PROJ_BBOX']

    @property
    def epsg(self) -> Optional[str]:
        return self.metadata['crs'].to_epsg()

    @property
    def metadata_dict(self):
        ''' match s2 l2a cogs from https://earth-search.aws.element84.com/v0 '''
        sentinel_metadata = {
            'sentinel:utm_zone': self.metadata['TILE_ID'][:2],
            'sentinel:latitude_band': self.metadata['TILE_ID'][2],
            'sentinel:grid_square': self.metadata['TILE_ID'][3:],
            'sentinel:product_ids': self.grd_ids,
            'sentinel:data_coverage': self.metadata['VALID_PIXEL_PERCENT'],
        }
        return sentinel_metadata

    @property
    def asset_dict(self):
        ''' map image_path (geotif) to pystac.Asset fields '''
        asset_dict = {
            'Gamma0_VV.tif':
            dict(key='gamma0_vv',
                 title='Gamma0 VV backscatter',
                 roles=['data', 'gamma0']),
            'Gamma0_VH.tif':
            dict(key='gamma0_vh',
                 title='Gamma0 VH backscatter',
                 roles=['data', 'gamma0']),
            'local_incident_angle.tif':
            dict(key='incidence',
                 title='Local incidence angle',
                 roles=['data', 'local-incidence-angle'])
        }

        return asset_dict
