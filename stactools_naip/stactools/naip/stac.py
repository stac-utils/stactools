import os
from typing import List

import pystac
from pystac.utils import str_to_datetime
from shapely.geometry import box, mapping, shape
import utm_zone as utm

from stactools.core.projection import epsg_from_utm_zone_number
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
                    "gsd": 1.0,
                    "roles": ["data"],
                    "title": "RGBIR COG tile",
                    "type": pystac.MediaType.COG
                },
            }
        })

    return collection


def create_item(state,
                fgdc_metadata_href,
                cog_href,
                thumbnail_href=None,
                additional_providers=None):
    """Creates a STAC Item from NAIP data.

    Args:
        state (str): The 2-letter state code for the state this item belongs to.
        fgdc_metadata_href (str): The href to the FGDC metadata
            for this NAIP scene.
        cog_href (str): The href to the image as a COG.
        thumbnail_href (str): Optional href for a thumbnail for this scene.
        additional_providers(List[pystac.Provider]): Optional list of additional
            providers to the USDA that will be included on this Item.

    This function will read the metadata file for information to place in
    the STAC item.

    Returns:
        pystac.Item: A STAC Item representing this NAIP scene.
    """
    fgdc_metadata_text = pystac.STAC_IO.read_text(fgdc_metadata_href)
    fgdc = parse_fgdc_metadata(fgdc_metadata_text)

    if 'Distribution_Information' in fgdc:
        resource_desc = fgdc['Distribution_Information'][
            'Resource_Description']
    else:
        resource_desc = os.path.basename(cog_href)
    item_id = naip_item_id(state, resource_desc)

    bbox_md = fgdc['Identification_Information']['Spatial_Domain'][
        'Bounding_Coordinates']

    xmin, xmax = float(bbox_md['West_Bounding_Coordinate']), float(
        bbox_md['East_Bounding_Coordinate'])
    ymin, ymax = float(bbox_md['South_Bounding_Coordinate']), float(
        bbox_md['North_Bounding_Coordinate'])
    geom = mapping(box(xmin, ymin, xmax, ymax))
    bounds = list(shape(geom).bounds)

    dt = str_to_datetime(
        fgdc['Identification_Information']['Time_Period_of_Content']
        ['Time_Period_Information']['Single_Date/Time']['Calendar_Date'])

    item = pystac.Item(id=item_id,
                       geometry=geom,
                       bbox=bounds,
                       datetime=dt,
                       properties={'naip:state': state})

    # Common metadata
    item.common_metadata.providers = [constants.USDA_PROVIDER]
    if additional_providers is not None:
        item.common_metadata.providers.extend(additional_providers)
    item.common_metadata.gsd = 1.0

    # eo, for asset bands
    item.ext.enable('eo')

    # proj
    item.ext.enable('projection')
    # Some don't specify their UTM zone, some do.
    if 'Spatial_Reference_Information' in fgdc:
        utm_zone = fgdc['Spatial_Reference_Information'][
            'Horizontal_Coordinate_System_Definition']['Planar'][
                'Grid_Coordinate_System']['Universal_Transverse_Mercator'][
                    'UTM_Zone_Number']
        epsg = epsg_from_utm_zone_number(utm_zone, south=False)
    else:
        epsg = utm.epsg(geom)
    item.ext.projection.epsg = epsg

    # COG
    item.add_asset(
        'image',
        pystac.Asset(href=cog_href,
                     media_type=pystac.MediaType.COG,
                     roles=['data'],
                     title="RGBIR COG tile"))

    # Metadata
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
