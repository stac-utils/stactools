import os
import json
import re
from lxml import etree
from shapely.geometry import box, mapping, shape, Polygon
import pystac
from pystac.utils import (str_to_datetime, make_absolute_href)

from stactools.sentinel.utils import asset_key_from_path

SENTINEL_PROVIDER = pystac.Provider(
    name='ESA',
    roles=['producer', 'processor', 'licensor'],
    url='https://earth.esa.int/web/guest/home')


def create_item(item_path, additional_providers=None):
    safe_manifest_file_name = f"{item_path.rstrip('/')}/manifest.safe"

    with open(safe_manifest_file_name) as f:
        safe_manifest_tree = etree.parse(f)

    safe_manifest_root = safe_manifest_tree.getroot()

    # ESA manifest differs from sen2cor manifest for preview images
    thumbnail_element = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="Preview_4_Tile1_Data"]/byteStream/fileLocation',
        safe_manifest_root.nsmap)
    if thumbnail_element is None:
        thumbnail_element = safe_manifest_root.find(
            'dataObjectSection/dataObject[@ID="S2_Level-1C_Preview_Tile1_Data"]/byteStream/fileLocation',
            safe_manifest_root.nsmap)
    thumbnail_path = thumbnail_element.get('href')
    
    
    # ESA manifest differs from sen2cor manifest for granule metadata
    granule_metadata_element = safe_manifest_root.find(
    'dataObjectSection/dataObject[@ID="S2_Level-2A_Tile1_Metadata"]/byteStream/fileLocation',
    safe_manifest_root.nsmap)
    if granule_metadata_element is None:
        granule_metadata_element = safe_manifest_root.find(
            'dataObjectSection/dataObject[@ID="S2_Level-2A_Tile1_Data"]/byteStream/fileLocation',
            safe_manifest_root.nsmap)
    granule_metadata_path = granule_metadata_element.get('href')
    
    # MTD_MSIL2A.xml xpath is consistent
    l2a_metadata_path = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="S2_Level-2A_Product_Metadata"]/byteStream/fileLocation',
        safe_manifest_root.nsmap).get("href")

    inspire_metadata_path = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="INSPIRE_Metadata"]/byteStream/fileLocation',
        safe_manifest_root.nsmap).get("href")

    datastrip_metadata_path = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="S2_Level-2A_Datastrip1_Metadata"]/byteStream/fileLocation',
        safe_manifest_root.nsmap).get("href")


    thumbnail_asset = image_asset_from_path(thumbnail_path, item_path)
    l2a_metadata_asset = xml_asset_from_path(l2a_metadata_path, item_path)
    inspire_metadata_asset = xml_asset_from_path(inspire_metadata_path,
                                                 item_path)
    datastrip_metadata_asset = xml_asset_from_path(datastrip_metadata_path,
                                                   item_path)
    granule_metadata_asset = xml_asset_from_path(granule_metadata_path,
                                                 item_path)

    with open(os.path.join(item_path, clean_path(l2a_metadata_path,
                                                 "xml"))) as f:
        metadata_tree = etree.parse(f)

    metadata_root = metadata_tree.getroot()
    geometric_info = metadata_root.find('n1:Geometric_Info',
                                        metadata_root.nsmap)
    footprint_coords = [
        float(c) for c in geometric_info.find(
            'Product_Footprint/Product_Footprint/Global_Footprint/EXT_POS_LIST'
        ).text.split(' ') if c
    ]
    footprint_points = [
        p[::-1] for p in list(zip(*[iter(footprint_coords)] * 2))
    ]
    footprint_polygon = Polygon(footprint_points)
    geometry = mapping(footprint_polygon)
    bbox = footprint_polygon.bounds

    product_info = metadata_root.find('n1:General_Info/Product_Info',
                                      metadata_root.nsmap)
    product_uri = product_info.find('PRODUCT_URI').text
    dt = str_to_datetime(product_info.find('PRODUCT_START_TIME').text)

    orbit_number = product_info.find('Datatake/SENSING_ORBIT_NUMBER').text
    orbit_direction = product_info.find('Datatake/SENSING_ORBIT_DIRECTION').text

    granule = product_info.find('Product_Organisation/Granule_List/Granule')
    image_paths = granule.findall('IMAGE_FILE')
    image_assets = [
        image_asset_from_path(image_path.text, item_path)
        for image_path in image_paths
    ]

    with open(os.path.join(item_path, clean_path(granule_metadata_path, "xml"))) as f:
        granule_metadata_tree = etree.parse(f)
    granule_metadata_root = granule_metadata_tree.getroot()
    cloudy_percentage = granule_metadata_root

    item = pystac.Item(id=product_uri,
                       geometry=geometry,
                       bbox=bbox,
                       datetime=dt,
                       properties={})

    item.common_metadata.providers = [SENTINEL_PROVIDER]

    item.add_asset(*l2a_metadata_asset)
    item.add_asset(*inspire_metadata_asset)
    item.add_asset(*datastrip_metadata_asset)
    item.add_asset(*granule_metadata_asset)
    item.add_asset(*thumbnail_asset)

    for asset in image_assets:
        item.add_asset(*asset)

    item.ext.enable("eo")
    item.ext.eo.cloud_cover = 

    item.properties['sat:relative_orbit'] = orbit_number
    item.properties['sat:orbit_state'] = orbit_direction

    print('\n')
    print(json.dumps(item.to_dict()))
    print('\n')


def xml_asset_from_path(asset_path, base_path, add_extension=False):
    if add_extension:
        path = os.path.join(base_path, clean_path(asset_path, "xml"))
    else:
        path = os.path.join(base_path, asset_path)
    return (asset_key_from_path(asset_path),
            pystac.Asset(href=make_absolute_href(path),
                         media_type=pystac.MediaType.XML,
                         roles=['metadata']))


def image_asset_from_path(asset_path, base_path):
    # test for jp2 or tif or tiff
    jp2_path = os.path.join(base_path, clean_path(asset_path, "jp2"))
    tif_path_1 = os.path.join(base_path, clean_path(asset_path, "tif"))
    tif_path_2 = os.path.join(base_path, clean_path(asset_path, "tiff"))

    if os.path.exists(jp2_path):
        path = jp2_path
        media_type = pystac.MediaType.JPEG2000
    elif os.path.exists(tif_path_1):
        path = tif_path_1
        media_type = pystac.MediaType.TIFF
    elif os.path.exists(tif_path_2):
        path = tif_path_2
        media_type = pystac.MediaType.TIFF
    else:
        raise Exception(
            f"No JPG2000 or TIFF asset exists at location: {os.path.join(base_path, asset_path)}"
        )
    
    if "_"

    return (asset_key_from_path(asset_path),
            pystac.Asset(href=make_absolute_href(path),
                         media_type=media_type,
                         roles=['data']))


def clean_path(path, extension=None):
    extension = extension.strip(".")
    clean_path = path.lstrip(".").strip("/")
    regex = re.compile(rf'.{extension}$', re.IGNORECASE)
    if extension is not None:
        clean_path = f"{re.sub(regex, '', clean_path)}.{extension}"
    return clean_path
