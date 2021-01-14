import os
import xml.etree.ElementTree as ET

import pystac
from pystac.utils import str_to_datetime
from shapely.geometry import box, mapping, shape

from stactools.corine.constants import (COPERNICUS_PROVIDER,
                                        ITEM_TIF_IMAGE_NAME,
                                        ITEM_METADATA_NAME)


def create_item(metadata_href):
    """Creates a STAC Item from CORINE data.
    Args:
        metadata_href (str): The href to the metadata for this tif.
    This function will read the metadata file for information to place in
    the STAC item.
    Returns:
        pystac.Item: A STAC Item representing this CORINE Land Cover.
    """

    metadata_root = ET.parse(metadata_href).getroot()

    # Item id
    image_name_node = 'Esri/DataProperties/itemProps/itemName'
    image_name = metadata_root.find(image_name_node).text
    item_id = os.path.splitext(image_name)[0]

    # Bounding box
    bounding_box_node = 'dataIdInfo/dataExt/geoEle/GeoBndBox/{}'
    west_long = float(
        metadata_root.find(bounding_box_node.format('westBL')).text)
    east_long = float(
        metadata_root.find(bounding_box_node.format('eastBL')).text)
    south_lat = float(
        metadata_root.find(bounding_box_node.format('southBL')).text)
    north_lat = float(
        metadata_root.find(bounding_box_node.format('northBL')).text)

    geom = mapping(box(west_long, south_lat, east_long, north_lat))
    bounds = shape(geom).bounds

    # EPSG
    epsg_element = 'refSysInfo/RefSystem/refSysID/identCode'
    epsg = int(
        metadata_root.find(epsg_element).attrib['code'].replace('EPSG:', ''))

    # Item date
    id_dt_node = 'dataIdInfo/idCitation/date/pubDate'
    id_dt_text = metadata_root.find(id_dt_node).text
    id_dt = str_to_datetime(id_dt_text)

    # Title
    title_node = 'dataIdInfo/idCitation/resTitle'
    title_text = metadata_root.find(title_node).text

    item = pystac.Item(id=item_id,
                       geometry=geom,
                       bbox=bounds,
                       datetime=id_dt,
                       properties={'corine:title': title_text})

    # Common metadata
    item.common_metadata.providers = [COPERNICUS_PROVIDER]

    # proj
    item.ext.enable('projection')
    item.ext.projection.epsg = epsg

    # Tif
    item.add_asset(
        ITEM_TIF_IMAGE_NAME,
        pystac.Asset(href=image_name,
                     media_type=pystac.MediaType.TIFF,
                     roles=['data'],
                     title="tif image"))

    # Metadata
    item.add_asset(
        ITEM_METADATA_NAME,
        pystac.Asset(href=metadata_href,
                     media_type=pystac.MediaType.TEXT,
                     roles=['metadata'],
                     title='FGDC Metdata'))

    return item
