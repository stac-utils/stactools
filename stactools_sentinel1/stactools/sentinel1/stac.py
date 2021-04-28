from datetime import datetime
import logging
import os
from typing import List, Optional

import pystac
from pystac.extensions.sat import OrbitState

from stactools.sentinel1.rtc_metadata import RTCMetadata
from stactools.sentinel1 import constants as c

logger = logging.getLogger(__name__)


def create_collection() -> pystac.Collection:
    """Creates a STAC Collection for Sentinel-1 RTC
    """
    # Lists of all possible values for items
    summary_dict = {
        'constellation': [c.SENTINEL_CONSTELLATION],
        'platform': c.SENTINEL_PLATFORMS,
        'gsd': [c.SENTINEL_RTC_SAR['gsd']],
        'proj:epsg': c.SENTINEL_RTC_EPSGS,
    }

    collection = pystac.Collection(
        'sentinel1-rtc-aws',
        description=c.SENTINEL_RTC_DESCRIPTION,
        extent=c.SENTINEL_RTC_EXTENT,
        title='Sentinel-1 RTC CONUS',
        stac_extensions=['sar', 'sat', 'proj'],
        keywords=[
            'backscatter', 'radiometry', 'sentinel', 'copernicus', 'esa', 'sar'
        ],
        providers=[c.SENTINEL_PROVIDER, c.SENTINEL_RTC_PROVIDER],
        summaries=summary_dict,
    )

    return collection


def create_item(
    granule_href: str,
    additional_providers: Optional[List[pystac.Provider]] = None,
    include_grd_metadata: Optional[bool] = False,
) -> pystac.Item:
    """Create a STAC Item from a Sentinel-1 RTC S3 Key

    Arguments:
        granule_href: The HREF to the S3 Key for particular MGRS tile product
            e.g. : s3://sentinel-s1-rtc-indigo/tiles/RTC/1/IW/12/S/YJ/2016/S1B_20161121_12SYJ_ASC
        additional_providers: Optional list of additional providers to set into the Item
        include_grd_metadata: Boolean to include links to original GRD metadata as STAC Assets

    Returns:
        pystac.Item: Item populated with STAC core and common extension metadata,
            from the Sentinel 1 RTC Geotiff files.
    """ # noqa
    product_metadata = RTCMetadata(granule_href)

    item = pystac.Item(id=product_metadata.product_id,
                       geometry=product_metadata.geometry,
                       bbox=product_metadata.bbox,
                       datetime=product_metadata.datetime,
                       properties={})

    # --Common metadata--
    # https://github.com/radiantearth/stac-spec/blob/master/item-spec/common-metadata.md
    item.common_metadata.providers = [
        c.SENTINEL_PROVIDER, c.SENTINEL_RTC_PROVIDER
    ]

    if additional_providers is not None:
        item.common_metadata.providers.extend(additional_providers)

    item.common_metadata.constellation = c.SENTINEL_CONSTELLATION
    item.common_metadata.platform = product_metadata.platform
    item.common_metadata.instruments = c.SENTINEL_INSTRUMENTS
    item.common_metadata.gsd = c.SENTINEL_RTC_SAR['gsd']

    item.common_metadata.start_datetime = product_metadata.start_datetime
    item.common_metadata.end_datetime = product_metadata.end_datetime

    # STAC Metadata creation date
    item.common_metadata.created = datetime.utcnow()

    # Addtional properties no belonging to extensions
    item.properties.update(**product_metadata.metadata_dict)

    # --Extensions--
    # SAR https://github.com/stac-extensions/sar
    item.ext.enable('sar')
    item.ext.sar.frequency_band = c.SENTINEL_FREQUENCY_BAND
    item.ext.sar.center_frequency = c.SENTINEL_CENTER_FREQUENCY
    item.ext.sar.observation_direction = c.SENTINEL_OBSERVATION_DIRECTION
    item.ext.sar.instrument_mode = c.SENTINEL_RTC_SAR['instrument_mode']
    item.ext.sar.product_type = c.SENTINEL_RTC_SAR['product_type']
    item.ext.sar.polarizations = c.SENTINEL_RTC_SAR['polarizations']
    item.ext.sar.resolution_range = c.SENTINEL_RTC_SAR['resolution_range']
    item.ext.sar.resolution_azimuth = c.SENTINEL_RTC_SAR['resolution_azimuth']
    item.ext.sar.pixel_spacing_range = c.SENTINEL_RTC_SAR[
        'pixel_spacing_range']
    item.ext.sar.pixel_spacing_azimuth = c.SENTINEL_RTC_SAR[
        'pixel_spacing_azimuth']
    item.ext.sar.looks_equivalent_number = c.SENTINEL_RTC_SAR[
        'looks_equivalent_number']
    item.ext.sar.looks_range = c.SENTINEL_RTC_SAR['looks_range']
    item.ext.sar.looks_azimuth = c.SENTINEL_RTC_SAR['looks_azimuth']

    # SAT https://github.com/stac-extensions/sat
    item.ext.enable('sat')
    item.ext.sat.orbit_state = OrbitState(product_metadata.orbit_state.lower())
    item.ext.sat.relative_orbit = product_metadata.relative_orbit
    item.ext.sat.absolute_orbit = product_metadata.absolute_orbit

    # PROJECTION https://github.com/stac-extensions/projection
    item.ext.enable('projection')
    item.ext.projection.epsg = product_metadata.epsg
    item.ext.projection.shape = product_metadata.shape
    item.ext.projection.bbox = product_metadata.proj_bbox
    item.ext.projection.transform = product_metadata.metadata['transform']

    # Additional extensions could be useful, but not yet implemented in pystac:

    # MGRS https://github.com/stac-extensions/mgrs
    # item.ext.enable('mgrs')
    # item.ext.projection.utm_zone = product_metadata.metadata['TILE_ID'][:2]
    # item.ext.projection.latitude_band = product_metadata.metadata['TILE_ID'][2]
    # item.ext.projection.grid_square = product_metadata.metadata['TILE_ID'][3:]

    # RASTER https://github.com/stac-extensions/raster
    # To capture nodata value and incidence angle units and scaling
    # https://github.com/stac-extensions/raster#value-object

    # --Assets--

    # COGs
    for image in product_metadata.image_paths:
        asset_href = os.path.join(product_metadata.href, image)
        logger.debug(f'Creating asset for image {asset_href}')

        # https://github.com/stac-extensions/sar#best-practices
        asset = pystac.Asset(href=asset_href,
                             media_type=product_metadata.image_media_type,
                             title=product_metadata.asset_dict[image]['title'],
                             roles=product_metadata.asset_dict[image]['roles'])
        item.add_asset(product_metadata.asset_dict[image]['key'], asset)

    # Metadata
    if include_grd_metadata:
        for i, grd in enumerate(product_metadata.grd_ids):
            json_href = os.path.join(product_metadata.href, grd,
                                     'productInfo.json')
            asset = pystac.Asset(href=json_href,
                                 media_type=pystac.MediaType.JSON,
                                 title=f'{grd} JSON metadata',
                                 roles=['metadata'])
            item.add_asset(f'productInfo_{i}', asset)

            xml_href = os.path.join(product_metadata.href, grd,
                                    'manifest.safe')
            asset = pystac.Asset(href=xml_href,
                                 media_type=pystac.MediaType.XML,
                                 title=f'{grd} XML metadata',
                                 roles=['metadata'])
            item.add_asset(f'manifest_{i}', asset)

    # --Links--
    # item.links.append(c.SENTINEL_LICENSE)
    item.links.append(c.SENTINEL_RTC_LICENSE)

    return item
