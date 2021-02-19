import os
from typing import List, Optional

import dateutil.parser
import pystac
from pystac.utils import str_to_datetime
from shapely.geometry import shape, box, mapping
import rasterio as rio

from stactools.core.projection import reproject_geom
from stactools.naip import constants
from stactools.naip.utils import parse_fgdc_metadata


def naip_item_id(state, resource_name):
    """Generates a STAC Item ID based on the state and the "Resource Description"
    contained in the FGDC metadata.

    Args:
        state (str): The two-letter state code for the state this belongs to.
        resource_name (str): The resource name, e.g. m_3008501_ne_16_1_20110815_20111017.tif

    Returns:
        str: The STAC ID to use for this scene.
    """

    return '{}_{}'.format(state, os.path.splitext(resource_name)[0])


def create_collection(seasons: List[int]) -> pystac.Collection:
    """Creates a STAC COllection for NAIP data.

    Args:
        seasons (List[int]): List of years that represent the NAIP seasons
            this collection represents.
    """
    extent = pystac.Extent(
        pystac.SpatialExtent(bboxes=[[-124.784, 24.744, -66.951, 49.346]]),
        pystac.TemporalExtent(intervals=[[
            pystac.utils.str_to_datetime(f"{min(seasons)}-01-01T00:00:00Z"),
            pystac.utils.str_to_datetime(f"{max(seasons)}-01-01T00:00:00Z")
        ]]))

    collection = pystac.Collection(
        id=constants.NAIP_ID,
        description=constants.NAIP_DESCRIPTION,
        title=constants.NAIP_TITLE,
        license=constants.NAIP_LICENSE,
        providers=[constants.USDA_PROVIDER],
        extent=extent,
        stac_extensions=['item-assets'],
        extra_fields={
            'item_assets': {
                'image': {
                    "eo:bands": [b.properties for b in constants.NAIP_BANDS],
                    "roles": ["data"],
                    "title": "RGBIR COG tile",
                    "type": pystac.MediaType.COG
                },
            }
        })

    return collection


def create_item(state,
                year,
                cog_href,
                fgdc_metadata_href: Optional[str],
                thumbnail_href=None,
                additional_providers=None):
    """Creates a STAC Item from NAIP data.

    Args:
        state (str): The 2-letter state code for the state this item belongs to.
        year (str): The NAIP year.
        fgdc_metadata_href (str): The href to the FGDC metadata
            for this NAIP scene. Optional, a some NAIP scenes to not have this
            (e.g. 2010)
        cog_href (str): The href to the image as a COG. This needs
            to be an HREF that rasterio is able to open.
        thumbnail_href (str): Optional href for a thumbnail for this scene.
        additional_providers(List[pystac.Provider]): Optional list of additional
            providers to the USDA that will be included on this Item.

    This function will read the metadata file for information to place in
    the STAC item.

    Returns:
        pystac.Item: A STAC Item representing this NAIP scene.
    """

    with rio.open(cog_href) as ds:
        gsd = ds.res[0]
        epsg = int(ds.crs.to_authority()[1])
        image_shape = list(ds.shape)
        original_bbox = list(ds.bounds)
        transform = list(ds.transform)
        geom = reproject_geom(ds.crs,
                              'epsg:4326',
                              mapping(box(*ds.bounds)),
                              precision=6)

    if fgdc_metadata_href is not None:
        fgdc_metadata_text = pystac.STAC_IO.read_text(fgdc_metadata_href)
        fgdc = parse_fgdc_metadata(fgdc_metadata_text)
    else:
        fgdc = {}

    if 'Distribution_Information' in fgdc:
        resource_desc = fgdc['Distribution_Information'][
            'Resource_Description']
    else:
        resource_desc = os.path.basename(cog_href)
    item_id = naip_item_id(state, resource_desc)

    bounds = list(shape(geom).bounds)

    if any(fgdc):
        dt = str_to_datetime(
            fgdc['Identification_Information']['Time_Period_of_Content']
            ['Time_Period_Information']['Single_Date/Time']['Calendar_Date'])
    else:
        fname = os.path.splitext(os.path.basename(cog_href))[0]
        fname_date = fname.split('_')[5]
        dt = dateutil.parser.isoparse(fname_date)

    properties = {'naip:state': state, 'naip:year': year}

    item = pystac.Item(id=item_id,
                       geometry=geom,
                       bbox=bounds,
                       datetime=dt,
                       properties=properties)

    # Common metadata
    item.common_metadata.providers = [constants.USDA_PROVIDER]
    if additional_providers is not None:
        item.common_metadata.providers.extend(additional_providers)
    item.common_metadata.gsd = gsd

    # eo, for asset bands
    item.ext.enable('eo')

    # proj
    item.ext.enable('projection')
    item.ext.projection.epsg = epsg
    item.ext.projection.shape = image_shape
    item.ext.projection.bbox = original_bbox
    item.ext.projection.transform = transform

    # COG
    item.add_asset(
        'image',
        pystac.Asset(href=cog_href,
                     media_type=pystac.MediaType.COG,
                     roles=['data'],
                     title="RGBIR COG tile"))

    # Metadata
    if any(fgdc):
        item.add_asset(
            'metadata',
            pystac.Asset(href=fgdc_metadata_href,
                         media_type=pystac.MediaType.TEXT,
                         roles=['metadata'],
                         title='FGDC Metdata'))

    if thumbnail_href is not None:
        media_type = pystac.MediaType.JPEG
        if thumbnail_href.lower().endswith('png'):
            media_type = pystac.MediaType.PNG
        item.add_asset(
            'thumbnail',
            pystac.Asset(href=thumbnail_href,
                         media_type=media_type,
                         roles=['thumbnail'],
                         title='Thumbnail'))

    item.ext.eo.set_bands(constants.NAIP_BANDS, item.assets['image'])

    return item
