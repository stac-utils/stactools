import os
import re
from shapely.geometry import mapping, Polygon
import pystac
from pystac.utils import (str_to_datetime, make_absolute_href)

from stactools.sentinel.utils import (mtd_asset_key_from_path, clean_path,
                                      open_xml_file_root, get_xml_node_attr,
                                      get_xml_node_text, list_xml_node,
                                      band_index_to_name, mgrs_from_path,
                                      get_xml_node)
from stactools.sentinel.constants import (SENTINEL_PROVIDER, SENTINEL_LICENSE,
                                          SENTINEL_BANDS, SENTINEL_INSTRUMENTS,
                                          SENTINEL_CONSTELLATION)


def create_item(item_path, target_path, additional_providers=None):
    safe_manifest_path = 'manifest.safe'
    safe_manifest_root = open_xml_file_root(
        os.path.join(item_path, safe_manifest_path))

    thumbnail_path = thumbnail_path_from_safe_manifest(safe_manifest_root)

    (l2a_mtd_path, inspire_mtd_path, datastrip_mtd_path,
     granule_mtd_path) = mtd_paths_from_safe_manifest(safe_manifest_root)

    safe_manifest_asset = xml_asset_from_path(safe_manifest_path, item_path)
    l2a_mtd_asset = xml_asset_from_path(l2a_mtd_path, item_path)
    inspire_mtd_asset = xml_asset_from_path(inspire_mtd_path, item_path)
    datastrip_mtd_asset = xml_asset_from_path(datastrip_mtd_path, item_path)
    granule_mtd_asset = xml_asset_from_path(granule_mtd_path, item_path)

    l2a_mtd = parse_l2a_mtd(item_path, l2a_mtd_path)
    granule_mtd = parse_granule_mtd(item_path, granule_mtd_path)
    mgrs_mtd = {'s2:mgrs_tile': mgrs_from_path(item_path)}

    constant_properties = {
        'constellation': SENTINEL_CONSTELLATION,
        'instruments': SENTINEL_INSTRUMENTS,
    }

    all_metadata = {
        **constant_properties,
        **l2a_mtd,
        **granule_mtd,
        **mgrs_mtd
    }

    # metadata that should not be included in the item properies is prepended with 'x:'
    all_properties = {
        k: all_metadata[k]
        for k in all_metadata if not k.startswith('x:')
    }
    short_properties = {
        k: all_properties[k]
        for k in all_properties if not k.startswith('s2:')
    }

    item = pystac.Item(id=l2a_mtd['s2:product_uri'],
                       geometry=l2a_mtd['x:geometry'],
                       bbox=l2a_mtd['x:bbox'],
                       datetime=l2a_mtd['x:dt'],
                       properties=short_properties)

    item.ext.enable('eo')

    item.common_metadata.providers = [SENTINEL_PROVIDER]

    if additional_providers is not None:
        item.common_metadata.providers.extend(additional_providers)

    thumbnail_asset = image_asset_from_path(thumbnail_path, item_path, item)

    image_assets = [
        image_asset_from_path(image_path.text, item_path, item)
        for image_path in l2a_mtd['x:image_paths']
    ]

    item.add_asset(*safe_manifest_asset)
    item.add_asset(*l2a_mtd_asset)
    item.add_asset(*inspire_mtd_asset)
    item.add_asset(*datastrip_mtd_asset)
    item.add_asset(*granule_mtd_asset)
    item.add_asset(*thumbnail_asset)

    for asset in image_assets:
        item.add_asset(*asset)

    item.ext.eo.cloud_cover = granule_mtd['x:cloudy_percentage']

    # TODO: when pystac SAT extension support is fixed, do this addition through the extension
    item.stac_extensions.append('sat')

    item.links.append(SENTINEL_LICENSE)

    item_path = make_absolute_href(os.path.join(target_path,
                                                f'{item.id}.json'))
    extended_item_path = make_absolute_href(
        os.path.join(target_path, f'{item.id}.extended.json'))

    extended_item = item.clone()
    extended_item.properties.update(all_properties)

    item.set_self_href(item_path)
    extended_item.set_self_href(extended_item_path)

    item.add_link(
        pystac.Link('extended-by', extended_item, pystac.MediaType.JSON))
    extended_item.add_link(pystac.Link('extends', item, pystac.MediaType.JSON))

    return (item, extended_item)


def parse_l2a_mtd(item_path, mtd_path):
    root = open_xml_file_root(
        os.path.join(item_path, clean_path(mtd_path, 'xml')))
    product_info_node = get_xml_node(root, 'n1:General_Info/Product_Info')
    datatake_node = get_xml_node(product_info_node, 'Datatake')
    granule_node = get_xml_node(product_info_node,
                                'Product_Organisation/Granule_List/Granule')
    reflectance_conversion_node = get_xml_node(
        root,
        'n1:General_Info/Product_Image_Characteristics/Reflectance_Conversion')
    qa_node = get_xml_node(root, 'n1:Quality_Indicators_Info')
    bbox, geometry = geometry_from_l2a_mtd(root)
    metadata = {
        'x:bbox':
        bbox,
        'x:geometry':
        geometry,
        's2:product_uri':
        get_xml_node_text(product_info_node, 'PRODUCT_URI'),
        's2:generation_time':
        get_xml_node_text(product_info_node, 'GENERATION_TIME'),
        's2:processing_baseline':
        get_xml_node_text(product_info_node, 'PROCESSING_BASELINE'),
        's2:product_type':
        get_xml_node_text(product_info_node, 'PRODUCT_TYPE'),
        'x:dt':
        str_to_datetime(
            get_xml_node_text(product_info_node, 'PRODUCT_START_TIME')),
        's2:datatake_id':
        get_xml_node_attr(datatake_node, 'datatakeIdentifier'),
        's2:datatake_type':
        get_xml_node_text(datatake_node, 'DATATAKE_TYPE'),
        'sat:relative_orbit':
        int(get_xml_node_text(datatake_node, 'SENSING_ORBIT_NUMBER')),
        'sat:orbit_state':
        get_xml_node_text(datatake_node, 'SENSING_ORBIT_DIRECTION'),
        'platform':
        get_xml_node_text(datatake_node, 'SPACECRAFT_NAME'),
        's2:datastrip_id':
        get_xml_node_attr(granule_node, 'datastripIdentifier'),
        's2:granule_id':
        get_xml_node_attr(granule_node, 'granuleIdentifier'),
        'x:image_paths':
        list_xml_node(granule_node, 'IMAGE_FILE'),
        's2:reflectance_conversion_factor':
        float(get_xml_node_text(reflectance_conversion_node, 'U')),
        's2:cloud_coverage_assessment':
        float(get_xml_node_text(qa_node, 'Cloud_Coverage_Assessment')),
        's2:degraded_msi_data_percentage':
        float(
            get_xml_node_text(
                root,
                'n1:Quality_Indicators_Info/Technical_Quality_Assessment/' +
                'DEGRADED_MSI_DATA_PERCENTAGE')),
    }

    irradiance_nodes = list_xml_node(reflectance_conversion_node,
                                     'Solar_Irradiance_List/SOLAR_IRRADIANCE')

    for node in irradiance_nodes:
        metadata.update(solar_irradiance_from_node(node))

    return metadata


def parse_granule_mtd(item_path, mtd_path):
    root = open_xml_file_root(
        os.path.join(item_path, clean_path(mtd_path, 'xml')))
    tile_angles_node = get_xml_node(root, 'n1:Geometric_Info/Tile_Angles')
    viewing_angle_nodes = list_xml_node(
        tile_angles_node,
        'Mean_Viewing_Incidence_Angle_List/Mean_Viewing_Incidence_Angle')

    metadata = {
        'x:cloudy_percentage':
        float(
            get_xml_node_text(
                root,
                'n1:Quality_Indicators_Info/Image_Content_QI/CLOUDY_PIXEL_PERCENTAGE'
            )),
        's2:mean_solar_zenith':
        float(
            get_xml_node_text(tile_angles_node,
                              'Mean_Sun_Angle/ZENITH_ANGLE')),
        's2:mean_solar_azimuth':
        float(
            get_xml_node_text(tile_angles_node,
                              'Mean_Sun_Angle/AZIMUTH_ANGLE'))
    }

    for node in viewing_angle_nodes:
        metadata.update(mean_incidence_angles_from_node(node))

    return metadata


def thumbnail_path_from_safe_manifest(safe_manifest_root):
    # ESA manifest differs from sen2cor manifest for preview images
    thumbnail_element = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="S2_Level-1C_Preview_Tile1_Data"]/' +
        'byteStream/fileLocation', safe_manifest_root.nsmap)
    if thumbnail_element is None:
        thumbnail_element = safe_manifest_root.find(
            'dataObjectSection/dataObject[@ID="Preview_4_Tile1_Data"]/' +
            'byteStream/fileLocation', safe_manifest_root.nsmap)
    return thumbnail_element.get('href')


def mtd_paths_from_safe_manifest(safe_manifest_root):
    l2a_mtd_path = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="S2_Level-2A_Product_Metadata"]/' +
        'byteStream/fileLocation', safe_manifest_root.nsmap).get('href')

    inspire_mtd_path = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="INSPIRE_Metadata"]/' +
        'byteStream/fileLocation', safe_manifest_root.nsmap).get('href')

    datastrip_mtd_path = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="S2_Level-2A_Datastrip1_Metadata"]/'
        + 'byteStream/fileLocation', safe_manifest_root.nsmap).get('href')
    granule_mtd_element = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="S2_Level-2A_Tile1_Data"]/' +
        'byteStream/fileLocation', safe_manifest_root.nsmap)
    if granule_mtd_element is None:
        granule_mtd_element = safe_manifest_root.find(
            'dataObjectSection/dataObject[@ID="S2_Level-2A_Tile1_Metadata"]/' +
            'byteStream/fileLocation', safe_manifest_root.nsmap)
    granule_mtd_path = granule_mtd_element.get('href')

    return (l2a_mtd_path, inspire_mtd_path, datastrip_mtd_path,
            granule_mtd_path)


def geometry_from_l2a_mtd(l2a_mtd_root):
    geometric_info = l2a_mtd_root.find('n1:Geometric_Info', l2a_mtd_root.nsmap)
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
    return (bbox, geometry)


def mean_incidence_angles_from_granule_mtd(granule_mtd_root):
    angle_nodes = list_xml_node(
        granule_mtd_root,
        'n1:Geometric_Info/Tile_Angles/Mean_Viewing_Incidence_Angle_List/' +
        'Mean_Viewing_Incidence_Angle')
    all_angles = {}
    for node in angle_nodes:
        all_angles.update(mean_incidence_angles_from_node(node))
    return all_angles


def mean_incidence_angles_from_node(node):
    band_name = band_index_to_name(int(node.get('bandId')))
    zenith_key = f's2:meanIncidenceZenithAngle{band_name}'
    azimuth_key = f's2:meanIncidenceAzimuthAngle{band_name}'
    zenith = float(node.find('ZENITH_ANGLE').text)
    azimuth = float(node.find('AZIMUTH_ANGLE').text)
    return {zenith_key: zenith, azimuth_key: azimuth}


def solar_irradiance_from_node(node):
    band_name = band_index_to_name(int(node.get('bandId')))
    key = f's2:solarIrradiance{band_name}'
    value = float(node.text)
    return {key: value}


def xml_asset_from_path(asset_path, base_path, add_extension=False):
    if add_extension:
        path = os.path.join(base_path, clean_path(asset_path, 'xml'))
    else:
        path = os.path.join(base_path, asset_path)
    return (mtd_asset_key_from_path(asset_path),
            pystac.Asset(href=make_absolute_href(path),
                         media_type=pystac.MediaType.XML,
                         roles=['metadata']))


def image_asset_from_path(asset_path, base_path, item):
    # test for jp2 or tif or tiff
    jp2_path = os.path.join(base_path, clean_path(asset_path, 'jp2'))
    tif_path_1 = os.path.join(base_path, clean_path(asset_path, 'tif'))
    tif_path_2 = os.path.join(base_path, clean_path(asset_path, 'tiff'))

    if os.path.exists(jp2_path):
        path = jp2_path
        media_type = pystac.MediaType.JPEG2000
    elif os.path.exists(tif_path_1):
        path = tif_path_1
        media_type = pystac.MediaType.GEOTIFF
    elif os.path.exists(tif_path_2):
        path = tif_path_2
        media_type = pystac.MediaType.GEOTIFF
    else:
        raise Exception(
            f'No JP2 or TIFF asset exists at location: {os.path.join(base_path, asset_path)}'
        )

    band_id_search = re.search(r'_(B\w{2})_', path)

    if band_id_search is not None:
        band_id = band_id_search.group(1)
        band = SENTINEL_BANDS[band_id]
        asset = pystac.Asset(href=make_absolute_href(path),
                             media_type=media_type,
                             title=band.description,
                             roles=['data'],
                             properties={'gsd': float(path[-7:-5])})
        item.ext.eo.set_bands([SENTINEL_BANDS[band_id]], asset)
        return (asset_path[-7:].replace('_', '-'), asset)
    elif '_PVI' in path:
        asset = pystac.Asset(href=make_absolute_href(path),
                             media_type=media_type,
                             title='True color preview',
                             roles=['data'])
        item.ext.eo.set_bands([
            SENTINEL_BANDS['B04'], SENTINEL_BANDS['B03'], SENTINEL_BANDS['B02']
        ], asset)
        return ('preview', asset)
    elif '_TCI_' in path:
        asset = pystac.Asset(href=make_absolute_href(path),
                             media_type=media_type,
                             title='True color image',
                             roles=['data'],
                             properties={'gsd': float(path[-7:-5])})
        item.ext.eo.set_bands([
            SENTINEL_BANDS['B04'], SENTINEL_BANDS['B03'], SENTINEL_BANDS['B02']
        ], asset)
        return (f'visual-{path[-7:-4]}', asset)
    elif '_AOT_' in path:
        asset = pystac.Asset(href=make_absolute_href(path),
                             media_type=media_type,
                             title='Aerosol optical thickness (AOT)',
                             roles=['data'],
                             properties={'gsd': float(path[-7:-5])})
        return (f'AOT-{path[-7:-4]}', asset)
    elif '_WVP_' in path:
        asset = pystac.Asset(href=make_absolute_href(path),
                             media_type=media_type,
                             title='Water vapour (WVP)',
                             roles=['data'],
                             properties={'gsd': float(path[-7:-5])})
        return (f'WVP-{path[-7:-4]}', asset)
    elif '_SCL_' in path:
        asset = pystac.Asset(href=make_absolute_href(path),
                             media_type=media_type,
                             title='Scene classfication map (SCL)',
                             roles=['data'],
                             properties={'gsd': float(path[-7:-5])})
        return (f'SCL-{path[-7:-4]}', asset)
    return (mtd_asset_key_from_path(asset_path),
            pystac.Asset(href=make_absolute_href(path),
                         media_type=media_type,
                         roles=['data']))
