import os
import re
from shapely.geometry import mapping, Polygon
import pystac
from pystac.utils import (str_to_datetime, make_absolute_href)

from stactools.sentinel.utils import (mtd_asset_key_from_path, clean_path,
                                      open_xml_file_root, get_xml_node_attr,
                                      get_xml_node_text, list_xml_node,
                                      band_index_to_name, mgrs_from_path)
from stactools.sentinel.constants import (SENTINEL_PROVIDER, SENTINEL_LICENSE,
                                          SENTINEL_BANDS, SENTINEL_INSTRUMENTS,
                                          SENTINEL_CONSTELLATION)


def create_item(item_path, additional_providers=None):
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

    l2a_mtd_root = open_xml_file_root(
        os.path.join(item_path, clean_path(l2a_mtd_path, 'xml')))
    bbox, geometry = geometry_from_l2a_mtd(l2a_mtd_root)

    mgrs_pos = mgrs_from_path(item_path)
    product_uri = get_xml_node_text(
        l2a_mtd_root, 'n1:General_Info/Product_Info/PRODUCT_URI')
    generation_time = get_xml_node_text(
        l2a_mtd_root, 'n1:General_Info/Product_Info/GENERATION_TIME')
    processing_baseline = get_xml_node_text(
        l2a_mtd_root, 'n1:General_Info/Product_Info/PROCESSING_BASELINE')
    product_type = get_xml_node_text(
        l2a_mtd_root, 'n1:General_Info/Product_Info/PRODUCT_TYPE')
    dt = str_to_datetime(
        get_xml_node_text(l2a_mtd_root,
                          'n1:General_Info/Product_Info/PRODUCT_START_TIME'))
    datatake_id = get_xml_node_attr(l2a_mtd_root,
                                    'n1:General_Info/Product_Info/Datatake',
                                    'datatakeIdentifier')
    orbit_number = int(
        get_xml_node_text(
            l2a_mtd_root,
            'n1:General_Info/Product_Info/Datatake/SENSING_ORBIT_NUMBER'))
    orbit_direction = get_xml_node_text(
        l2a_mtd_root,
        'n1:General_Info/Product_Info/Datatake/SENSING_ORBIT_DIRECTION')
    platform = get_xml_node_text(
        l2a_mtd_root, 'n1:General_Info/Product_Info/Datatake/SPACECRAFT_NAME')
    datatake_type = get_xml_node_text(
        l2a_mtd_root, 'n1:General_Info/Product_Info/Datatake/DATATAKE_TYPE')
    datastrip_id = get_xml_node_attr(
        l2a_mtd_root,
        'n1:General_Info/Product_Info/Product_Organisation/Granule_List/Granule',
        'datastripIdentifier')
    granule_id = get_xml_node_attr(
        l2a_mtd_root,
        'n1:General_Info/Product_Info/Product_Organisation/Granule_List/Granule',
        'granuleIdentifier')
    image_paths = list_xml_node(
        l2a_mtd_root,
        'n1:General_Info/Product_Info/Product_Organisation/Granule_List/Granule/IMAGE_FILE'
    )
    reflectance_conversion_factor = float(
        get_xml_node_text(
            l2a_mtd_root,
            'n1:General_Info/Product_Image_Characteristics/Reflectance_Conversion/U'
        ))
    cloud_coverage_assessment = float(
        get_xml_node_text(
            l2a_mtd_root,
            'n1:Quality_Indicators_Info/Cloud_Coverage_Assessment'))
    # degraded_msi_data_percentage = float(
    #     get_xml_node_text(
    #         l2a_mtd_root,
    #         'n1:Quality_Indicators_Info/Technical_Quality_Assessment/DEGRADED_MSI_DATA_PERCENTAGE'
    #     ))
    irradiance_props = solar_irradiance_values_from_l2a_mtd(l2a_mtd_root)
    granule_mtd_root = open_xml_file_root(
        os.path.join(item_path, clean_path(granule_mtd_path, 'xml')))
    cloudy_percentage = float(
        get_xml_node_text(
            granule_mtd_root,
            'n1:Quality_Indicators_Info/Image_Content_QI/CLOUDY_PIXEL_PERCENTAGE'
        ))
    mean_solar_zenith = float(
        get_xml_node_text(
            granule_mtd_root,
            'n1:Geometric_Info/Tile_Angles/Mean_Sun_Angle/ZENITH_ANGLE'))
    mean_solar_azimuth = float(
        get_xml_node_text(
            granule_mtd_root,
            'n1:Geometric_Info/Tile_Angles/Mean_Sun_Angle/AZIMUTH_ANGLE'))
    incidence_angle_props = mean_incidence_angles_from_granule_mtd(
        granule_mtd_root)

    properties = {
        'constellation': SENTINEL_CONSTELLATION,
        'platform': platform,
        'instruments': SENTINEL_INSTRUMENTS,
        's2:generationTime': generation_time,
        's2:datatakeIdentifier': datatake_id,
        's2:datastripIdentifier': datastrip_id,
        's2:granuleIdentifier': granule_id,
        's2:datatakeType': datatake_type,
        's2:mgrsTile': mgrs_pos,
        's2:processingBaseline': processing_baseline,
        's2:productURI': product_uri,
        's2:productType': product_type,
        's2:cloudCoverageAssessment': cloud_coverage_assessment,
        's2:meanSolarZenith': mean_solar_zenith,
        's2:meanSolarAzimuth': mean_solar_azimuth,
        's2:reflectanceConversionFactor': reflectance_conversion_factor
    }

    properties.update(incidence_angle_props)
    properties.update(irradiance_props)

    item = pystac.Item(id=product_uri,
                       geometry=geometry,
                       bbox=bbox,
                       datetime=dt,
                       properties=properties)

    item.ext.enable('eo')

    item.common_metadata.providers = [SENTINEL_PROVIDER]
    if additional_providers is not None:
        item.common_metadata.providers.extend(additional_providers)

    thumbnail_asset = image_asset_from_path(thumbnail_path, item_path, item)

    image_assets = [
        image_asset_from_path(image_path.text, item_path, item)
        for image_path in image_paths
    ]

    item.add_asset(*safe_manifest_asset)
    item.add_asset(*l2a_mtd_asset)
    item.add_asset(*inspire_mtd_asset)
    item.add_asset(*datastrip_mtd_asset)
    item.add_asset(*granule_mtd_asset)
    item.add_asset(*thumbnail_asset)

    for asset in image_assets:
        item.add_asset(*asset)

    item.ext.eo.cloud_cover = cloudy_percentage

    # TODO: when pystac SAT extension support is fixed, do this addition through the extension
    item.properties['sat:relative_orbit'] = orbit_number
    item.properties['sat:orbit_state'] = orbit_direction
    item.stac_extensions.append('sat')

    item.links.append(SENTINEL_LICENSE)

    return item


def thumbnail_path_from_safe_manifest(safe_manifest_root):
    # ESA manifest differs from sen2cor manifest for preview images
    thumbnail_element = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="Preview_4_Tile1_Data"]/' +
        'byteStream/fileLocation', safe_manifest_root.nsmap)
    if thumbnail_element is None:
        thumbnail_element = safe_manifest_root.find(
            'dataObjectSection/dataObject[@ID="S2_Level-1C_Preview_Tile1_Data"]/'
            + 'byteStream/fileLocation', safe_manifest_root.nsmap)
    return thumbnail_element.get('href')


def mtd_paths_from_safe_manifest(safe_manifest_root):
    l2a_mtd_path = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="S2_Level-2A_Product_Metadata"]/' +
        'byteStream/fileLocation', safe_manifest_root.nsmap).get('href')

    inspire_mtd_path = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="INSPIRE_Metadata"]/' +
        'byteStream/fileLocation', safe_manifest_root.nsmap).get('href')

    granule_mtd_element = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="S2_Level-2A_Tile1_Metadata"]/' +
        'byteStream/fileLocation', safe_manifest_root.nsmap)
    datastrip_mtd_path = safe_manifest_root.find(
        'dataObjectSection/dataObject[@ID="S2_Level-2A_Datastrip1_Metadata"]/'
        + 'byteStream/fileLocation', safe_manifest_root.nsmap).get('href')
    if granule_mtd_element is None:
        granule_mtd_element = safe_manifest_root.find(
            'dataObjectSection/dataObject[@ID="S2_Level-2A_Tile1_Data"]/' +
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


def solar_irradiance_values_from_l2a_mtd(l2a_mtd_root):
    irradiance_nodes = list_xml_node(
        l2a_mtd_root, 'n1:General_Info/Product_Image_Characteristics/' +
        'Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE')
    all_values = {}
    for node in irradiance_nodes:
        all_values.update(solar_irradiance_from_node(node))
    return all_values


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
