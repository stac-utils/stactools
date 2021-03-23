import xml.etree.ElementTree as ET

import pystac
from pystac.utils import str_to_datetime
from shapely.geometry import shape

from stactools.modis.constants import (ITEM_TIF_IMAGE_NAME, ITEM_METADATA_NAME,
                                       MODIS_CATALOG_ELEMENTS, MODIS_BAND_DATA,
                                       ADDITIONAL_MODIS_PROPERTIES)

def create_collection(catalog_id) -> pystac.Collection:
    """Creates a STAC Collection for MODIS data.
    """

    collection = pystac.Collection(
        id=catalog_id,
        description=MODIS_CATALOG_ELEMENTS[catalog_id].description,
        extent=MODIS_CATALOG_ELEMENTS[catalog_id].extent,
        title=MODIS_CATALOG_ELEMENTS[catalog_id].title,
        providers=MODIS_CATALOG_ELEMENTS[catalog_id].provider,
        stac_extensions=['item-assets'],
        extra_fields={
            'item_assets': {
                'image': {
                    "eo:bands": MODIS_BAND_DATA[catalog_id],
                    "roles": ["data"],
                    "title": "RGBIR COG tile",
                    "type": pystac.MediaType.COG
                },
            }
        })

    return collection

def create_item(metadata_href):
    """Creates a STAC Item from modis data.
    Args:
        metadata_href (str): The href to the metadata for this hdf.
    This function will read the metadata file for information to place in
    the STAC item.
    Returns:
        pystac.Item: A STAC Item representing this MODIS image.
    """

    metadata_root = ET.parse(metadata_href).getroot()

    # Item id
    name = metadata_root.find(
        'GranuleURMetaData/CollectionMetaData/ShortName').text
    version = metadata_root.find(
        'GranuleURMetaData/CollectionMetaData/VersionID').text
    short_item_id = '{}/00{}/{}'.format('MODIS', version, name)

    image_name = metadata_root.find(
        'GranuleURMetaData/DataFiles/DataFileContainer/DistributedFileName'
    ).text
    item_id = image_name.replace('.hdf', '')

    coordinates = []
    point_ele = '{}/{}'.format(
        'GranuleURMetaData/SpatialDomainContainer/',
        'HorizontalSpatialDomainContainer/GPolygon/Boundary/Point')
    for point in metadata_root.findall(point_ele):
        lon = float(point.find('PointLongitude').text)
        lat = float(point.find('PointLatitude').text)
        coordinates.append([lon, lat])

    geom = {'type': 'Polygon', 'coordinates': [coordinates]}

    bounds = shape(geom).bounds

    # Item date
    prod_node = 'GranuleURMetaData/ECSDataGranule/ProductionDateTime'
    prod_dt_text = metadata_root.find(prod_node).text
    prod_dt = str_to_datetime(prod_dt_text)

    item = pystac.Item(id=item_id,
                       geometry=geom,
                       bbox=bounds,
                       datetime=prod_dt,
                       properties=ADDITIONAL_MODIS_PROPERTIES[short_item_id])

    # Common metadata
    item.common_metadata.providers = [
        MODIS_CATALOG_ELEMENTS[short_item_id]['provider']
    ]
    item.common_metadata.description = MODIS_CATALOG_ELEMENTS[short_item_id][
        'description']

    item.common_metadata.instruments = [
        metadata_root.find(
            'GranuleURMetaData/Platform/Instrument/InstrumentShortName').text
    ]
    item.common_metadata.platform = metadata_root.find(
        'GranuleURMetaData/Platform/PlatformShortName').text
    item.common_metadata.title = MODIS_CATALOG_ELEMENTS[short_item_id]['title']

    # Hdf
    item.add_asset(
        ITEM_TIF_IMAGE_NAME,
        pystac.Asset(href=image_name,
                     media_type=pystac.MediaType.HDF,
                     roles=['data'],
                     title="hdf image"))

    # Metadata
    item.add_asset(
        ITEM_METADATA_NAME,
        pystac.Asset(href=image_name + '.xml',
                     media_type=pystac.MediaType.TEXT,
                     roles=['metadata'],
                     title='FGDC Metdata'))

    # Bands
    item.ext.enable('eo')

    if item_id in MODIS_BAND_DATA:
        item.ext.eo.bands = MODIS_BAND_DATA[item_id]

    return item
