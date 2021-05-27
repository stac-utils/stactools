import logging
import os
import re
from typing import Dict, List, Optional, Tuple

import pystac
from pystac.extensions.sat import OrbitState

from stactools.core.io import ReadHrefModifier
from stactools.core.projection import transform_from_bbox
from stactools.sentinel2.safe_manifest import SafeManifest
from stactools.sentinel2.product_metadata import ProductMetadata
from stactools.sentinel2.granule_metadata import GranuleMetadata
from stactools.sentinel2.utils import extract_gsd
from stactools.sentinel2.constants import (
    BANDS_TO_RESOLUTIONS, DATASTRIP_METADATA_ASSET_KEY, SENTINEL_PROVIDER,
    SENTINEL_LICENSE, SENTINEL_BANDS, SENTINEL_INSTRUMENTS,
    SENTINEL_CONSTELLATION, INSPIRE_METADATA_ASSET_KEY)

logger = logging.getLogger(__name__)


def create_item(
        granule_href: str,
        additional_providers: Optional[List[pystac.Provider]] = None,
        read_href_modifier: Optional[ReadHrefModifier] = None) -> pystac.Item:
    """Create a STC Item from a Sentinel 2 granule.

    Arguments:
        granule_href: The HREF to the granule. This is expected to be a path
            to a SAFE archive, e.g. : https://sentinel2l2a01.blob.core.windows.net/sentinel2-l2/01/C/CV/2016/03/27/S2A_MSIL2A_20160327T204522_N0212_R128_T01CCV_20210214T042702.SAFE
        additional_providers: Optional list of additional providers to set into the Item
        read_href_modifier: A function that takes an HREF and returns a modified HREF.
            This can be used to modify a HREF to make it readable, e.g. appending
            an Azure SAS token or creating a signed URL.

    Returns:
        pystac.Item: An item representing the Sentinel 2 scene
    """ # noqa

    safe_manifest = SafeManifest(granule_href, read_href_modifier)

    product_metadata = ProductMetadata(safe_manifest.product_metadata_href,
                                       read_href_modifier)
    granule_metadata = GranuleMetadata(safe_manifest.granule_metadata_href,
                                       read_href_modifier)

    item = pystac.Item(id=product_metadata.product_id,
                       geometry=product_metadata.geometry,
                       bbox=product_metadata.bbox,
                       datetime=product_metadata.datetime,
                       properties={})

    # --Common metadata--

    item.common_metadata.providers = [SENTINEL_PROVIDER]

    if additional_providers is not None:
        item.common_metadata.providers.extend(additional_providers)

    item.common_metadata.platform = product_metadata.platform
    item.common_metadata.constellation = SENTINEL_CONSTELLATION
    item.common_metadata.instruments = SENTINEL_INSTRUMENTS

    # --Extensions--

    # eo

    item.ext.enable('eo')
    item.ext.eo.cloud_cover = granule_metadata.cloudiness_percentage

    # sat

    item.ext.enable('sat')
    item.ext.sat.orbit_state = OrbitState(product_metadata.orbit_state.lower())
    item.ext.sat.relative_orbit = product_metadata.relative_orbit

    # proj
    item.ext.enable('projection')
    item.ext.projection.epsg = granule_metadata.epsg
    if item.ext.projection.epsg is None:
        raise ValueError(
            f'Could not determine EPSG code for {granule_href}; which is required.'
        )

    # s2 properties
    item.properties.update({
        **product_metadata.metadata_dict,
        **granule_metadata.metadata_dict
    })

    # --Assets--

    # Metadata

    item.add_asset(*safe_manifest.create_asset())
    item.add_asset(*product_metadata.create_asset())
    item.add_asset(*granule_metadata.create_asset())
    item.add_asset(
        INSPIRE_METADATA_ASSET_KEY,
        pystac.Asset(href=safe_manifest.inspire_metadata_href,
                     media_type=pystac.MediaType.XML,
                     roles=['metadata']))
    item.add_asset(
        DATASTRIP_METADATA_ASSET_KEY,
        pystac.Asset(href=safe_manifest.datastrip_metadata_href,
                     media_type=pystac.MediaType.XML,
                     roles=['metadata']))

    # Image assets
    proj_bbox = granule_metadata.proj_bbox

    image_assets = dict([
        image_asset_from_href(os.path.join(granule_href, image_path), item,
                              granule_metadata.resolution_to_shape, proj_bbox,
                              product_metadata.image_media_type)
        for image_path in product_metadata.image_paths
    ])

    for key, asset in image_assets.items():
        assert key not in item.assets
        item.add_asset(key, asset)

    # Thumbnail

    if safe_manifest.thumbnail_href is not None:
        item.add_asset(
            "preview",
            pystac.Asset(href=safe_manifest.thumbnail_href,
                         media_type=pystac.MediaType.COG,
                         roles=['thumbnail']))

    # --Links--

    item.links.append(SENTINEL_LICENSE)

    return item


def image_asset_from_href(
        asset_href: str,
        item: pystac.Item,
        resolution_to_shape: Dict[int, Tuple[int, int]],
        proj_bbox: List[float],
        media_type: Optional[str] = None) -> Tuple[str, pystac.Asset]:
    logger.debug(f'Creating asset for image {asset_href}')

    _, ext = os.path.splitext(asset_href)
    if media_type is not None:
        asset_media_type = media_type
    else:
        if ext.lower() == '.jp2':
            asset_media_type = pystac.MediaType.JPEG2000
        elif ext.lower() in ['.tiff', '.tif']:
            asset_media_type = pystac.MediaType.GEOTIFF
        else:
            raise Exception(
                f'Must supply a media type for asset : {asset_href}')

    # Handle preview image

    if '_PVI' in asset_href:
        asset = pystac.Asset(href=asset_href,
                             media_type=asset_media_type,
                             title='True color preview',
                             roles=['data'])
        item.ext.eo.set_bands([
            SENTINEL_BANDS['B04'], SENTINEL_BANDS['B03'], SENTINEL_BANDS['B02']
        ], asset)
        return ('preview', asset)

    # Extract gsd and proj info
    filename_gsd = extract_gsd(asset_href)
    shape = list(resolution_to_shape[int(filename_gsd)])
    transform = transform_from_bbox(proj_bbox, shape)

    def set_asset_properties(asset: pystac.Asset,
                             band_gsd: Optional[int] = None):
        if band_gsd:
            item.common_metadata.set_gsd(band_gsd, asset)
        item.ext.projection.set_shape(shape, asset)
        item.ext.projection.set_bbox(proj_bbox, asset)
        item.ext.projection.set_transform(transform, asset)

    # Handle band image

    band_id_search = re.search(r'_(B\w{2})', asset_href)
    if band_id_search is not None:
        band_id, href_res = os.path.splitext(asset_href)[0].split('_')[-2:]
        band = SENTINEL_BANDS[band_id]

        # Get the asset resolution from the file name.
        # If the asset resolution is the band GSD, then
        # include the gsd information for that asset. Otherwise,
        # do not include the GSD information in the asset
        # as this may be confusing for users given that the
        # raster spatial resolution and gsd will differ.
        # See https://github.com/radiantearth/stac-spec/issues/1096
        asset_res = int(href_res.replace('m', ''))
        band_gsd: Optional[int] = None
        if asset_res == BANDS_TO_RESOLUTIONS[band_id][0]:
            asset_key = band_id
            band_gsd = asset_res
        else:
            # If this isn't the default resolution, use the raster
            # resolution in the asset key.
            # TODO: Use the raster extension and spatial_resolution
            # property to encode the spatial resolution of all assets.
            asset_key = f'{band_id}_{asset_res}m'

        asset = pystac.Asset(href=asset_href,
                             media_type=asset_media_type,
                             title=f'{band.description} - {href_res}',
                             roles=['data'])

        item.ext.eo.set_bands([SENTINEL_BANDS[band_id]], asset)
        set_asset_properties(asset, band_gsd=band_gsd)
        return (asset_key, asset)

    # Handle auxiliary images

    if '_TCI_' in asset_href:
        # True color
        asset = pystac.Asset(href=asset_href,
                             media_type=asset_media_type,
                             title='True color image',
                             roles=['data'])
        item.ext.eo.set_bands([
            SENTINEL_BANDS['B04'], SENTINEL_BANDS['B03'], SENTINEL_BANDS['B02']
        ], asset)
        set_asset_properties(asset)
        return (f'visual-{asset_href[-7:-4]}', asset)

    if '_AOT_' in asset_href:
        # Aerosol
        asset = pystac.Asset(href=asset_href,
                             media_type=asset_media_type,
                             title='Aerosol optical thickness (AOT)',
                             roles=['data'])
        set_asset_properties(asset)
        return (f'AOT-{asset_href[-7:-4]}', asset)

    if '_WVP_' in asset_href:
        # Water vapor
        asset = pystac.Asset(href=asset_href,
                             media_type=asset_media_type,
                             title='Water vapour (WVP)',
                             roles=['data'])
        set_asset_properties(asset)
        return (f'WVP-{asset_href[-7:-4]}', asset)

    if '_SCL_' in asset_href:
        # Classification map
        asset = pystac.Asset(href=asset_href,
                             media_type=asset_media_type,
                             title='Scene classfication map (SCL)',
                             roles=['data'])
        set_asset_properties(asset)
        return (f'SCL-{asset_href[-7:-4]}', asset)

    raise ValueError(f'Unexpected asset: {asset_href}')
