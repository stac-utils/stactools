from datetime import datetime
from typing import List, Optional

import pystac
from pystac.utils import str_to_datetime

import rasterio
import geopandas as gpd
import os
import io
import json
import logging

logger = logging.getLogger(__name__)

class RTCMetadata:
    def __init__(self,
                 href):
        self.href = href

        def _load_metadata(asset='local_incident_angle.tif'):
            ''' key metadata stored in Geotiff tags '''
            with rasterio.Env(AWS_NO_SIGN_REQUEST='YES',
                              GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR') as env:
                with rasterio.open(os.path.join(href,asset)) as src:
                    metadata = src.profile
                    metadata.update(src.tags())
                    # other things that aren't keys in src.profile
                    metadata['PROJ_BBOX'] = list(src.bounds)
                    metadata['SHAPE'] = src.shape

            return metadata

        def _get_geometries():
            ''' bbox is MGRS grid square, but geometry is intersection of bbox
            and S1 frames use to create RTC product. EPSG:4326'''
            # NOTE: could also save proj:geometry in UTM CRS...
            gridfile = os.path.join(os.path.dirname(__file__),
                                    'sentinel1-rtc-conus-grid.geojson')
            gf = gpd.read_file(gridfile)
            gf.rename(columns=dict(id='tile'), inplace=True)
            gf_grid = gf[gf.tile == self.metadata['TILE_ID']]
            bbox = list(gf_grid.total_bounds)

            frames = []
            for i in range(1, int(self.metadata['NUMBER_SCENES'])+1):
                m = json.loads(self.metadata[f'SCENE_{i}_METADATA'])
                frames.append(gpd.read_file(io.StringIO(m['footprint'])))
            footprints = gpd.pd.concat(frames)

            intersection = gpd.overlay(gf_grid, footprints, how='intersection')
            valid_footprint = intersection.unary_union.convex_hull

            geometry = {"type": "Polygon",
                        "coordinates":[list(valid_footprint.exterior.coords)]}

            return (bbox, geometry)

        def _get_provinance():
            ''' RTC products are from mosaiced GRD frames '''
            # NOTE: return entire dictionary or just GRD frame names?
            grd_ids = []
            for i in range(1, int(self.metadata['NUMBER_SCENES'])+1):
                m = json.loads(self.metadata[f'SCENE_{i}_METADATA'])
                grd_ids.append(m['title'])

            return grd_ids

        def _get_times():
            ''' UTC start and end times of GRDs used in RTC product '''
            times = []
            for i in range(1, int(self.metadata['NUMBER_SCENES'])+1):
                m = json.loads(self.metadata[f'SCENE_{i}_METADATA'])
                times += [m['start_time'], m['end_time']]
                start = str_to_datetime(min(times))
                end = str_to_datetime(max(times))
                mid = start + (end - start)/2
            return start, mid, end

        self.metadata = _load_metadata()
        self.grd_ids = _get_provinance()
        self.start_datetime, self.datetime, self.end_datetime = _get_times()
        self.bbox, self.geometry = _get_geometries()

    @property
    def product_id(self) -> str:
        DATE = self.metadata['DATE'].replace('-','')
        orbNames = {'ascending':'ASC', 'descending':'DSC'}
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
        return ['Gamma0_VV.tif',
                'Gamma0_VH.tif',
                'local_incident_angle.tif']

    @property
    def absolute_orbit(self) -> Optional[int]:
        return int(self.metadata['ABSOLUTE_ORBIT_NUMBER'])

    @property
    def relative_orbit(self) -> Optional[int]:
        '''https://forum.step.esa.int/t/sentinel-1-relative-orbit-from-filename/7042 '''
        adjust = {'S1B':27, 'S1A':73}
        rel_orbit = ((self.absolute_orbit - adjust[self.metadata['MISSION_ID']]) % 175) + 1
        return

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
        'sentinel:latitude_band' : self.metadata['TILE_ID'][2],
        'sentinel:grid_square': self.metadata['TILE_ID'][3:],
        'sentinel:product_ids': self.grd_ids,
        'sentinel:data_coverage': self.metadata['VALID_PIXEL_PERCENT'],
        }
        return sentinel_metadata

    @property
    def asset_dict(self):
        ''' map image_path (geotif) to pystac.Asset fields '''
        asset_dict = {'Gamma0_VV.tif' : dict(key='gamma0_vv',
                                             title='Gamma0 VV backscatter',
                                             roles=['data','gamma0']),
                      'Gamma0_VH.tif' : dict(key='gamma0_vh',
                                             title='Gamma0 VH backscatter',
                                             roles=['data','gamma0']),
                      'local_incident_angle.tif' : dict(key='incidence',
                                                 title='Local incidence angle',
                                                 roles=['data','local-incidence-angle'])
                                                 }

        return asset_dict
