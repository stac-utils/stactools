import os

import pystac
from pystac.utils import str_to_datetime
import rasterio as rio
from shapely.geometry import box, mapping, shape

from stactools.cgls_lc100.constants import (
    PROVIDER_NAME, ITEM_TIF_IMAGE_NAME, DISCRETE_CLASSIFICATION_CLASS_NAMES,
    DISCRETE_CLASSIFICATION_CLASS_PALETTE)


def create_item(tif_href, additional_providers=None):
    """Creates a STAC Item from Copernicus Global Land Cover Layers data.
    Args:
        tif_href (str): The href to the metadata for this tif.
    This function will read the metadata file for information to place in
    the STAC item.
    Returns:
        pystac.Item: A STAC Item representing this Copernicus Global Land Cover Layers data.
    """

    with rio.open(tif_href) as f:
        tags = f.tags()
        band_tags = f.tags(1)
        bounds = f.bounds

    # Item id
    item_id = os.path.basename(tif_href).replace('.tif', '')

    # Bounds
    geom = mapping(box(bounds.left, bounds.bottom, bounds.right, bounds.top))
    bounds = shape(geom).bounds

    start_dt = str_to_datetime(tags.pop('time_coverage_start'))
    end_dt = str_to_datetime(tags.pop('time_coverage_end'))
    file_creation_dt = str_to_datetime(tags.pop('file_creation'))

    item = pystac.Item(id=item_id,
                       geometry=geom,
                       bbox=bounds,
                       datetime=None,
                       properties={
                           'start_datetime':
                           start_dt,
                           'end_datetime':
                           end_dt,
                           'discrete_classification_class_names':
                           DISCRETE_CLASSIFICATION_CLASS_NAMES,
                           'discrete_classification_class_palette':
                           DISCRETE_CLASSIFICATION_CLASS_PALETTE
                       })

    # Common metadata
    copernicus_provider = pystac.Provider(name=PROVIDER_NAME,
                                          url=(tags.pop('doi')),
                                          roles=['producer', 'licensor'])

    item.common_metadata.providers = [copernicus_provider]
    if additional_providers is not None:
        item.common_metadata.providers.extend(additional_providers)

    item.common_metadata.start_datetime = start_dt
    item.common_metadata.end_datetime = end_dt
    item.common_metadata.created = file_creation_dt

    item.common_metadata.description = tags.pop('Info')
    item.common_metadata.platform = tags.pop('platform')
    item.common_metadata.title = tags.pop('title')

    # proj
    item.ext.enable('projection')
    item.ext.projection.epsg = int(
        tags.pop('delivered_product_crs').replace('WGS84 (EPSG:',
                                                  '').replace(')', ''))

    # Extra fields
    for k, v in tags.items():
        item.extra_fields[k] = v

    # Bands
    long_name = band_tags.pop('long_name')
    band = pystac.extensions.eo.Band.create(
        name=long_name,
        common_name=band_tags.pop('short_name'),
        description=long_name)

    item.ext.enable('eo')
    item.ext.eo.bands = [band]

    # Tif
    item.add_asset(
        ITEM_TIF_IMAGE_NAME,
        pystac.Asset(href=tif_href,
                     media_type=pystac.MediaType.TIFF,
                     roles=['data'],
                     title="tif image"))
    return item
