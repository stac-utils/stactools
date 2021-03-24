from datetime import datetime
import re
from typing import List, Optional

from shapely.geometry import mapping, Polygon
import pystac
from pystac.utils import str_to_datetime

from stactools.sentinel2.constants import PRODUCT_METADATA_ASSET_KEY
from stactools.sentinel2.utils import (ReadHrefModifier, band_index_to_name,
                                       get_xml_node, get_xml_node_attr,
                                       get_xml_node_text, list_xml_node,
                                       read_xml, convert)


class ProductMetadata:
    def __init__(self,
                 href,
                 read_href_modifier: Optional[ReadHrefModifier] = None):
        self.href = href
        self._root = read_xml(href, read_href_modifier)
        self.product_info_node = get_xml_node(self._root,
                                              'n1:General_Info/Product_Info')
        self.datatake_node = get_xml_node(self.product_info_node, 'Datatake')
        self.granule_node = get_xml_node(
            self.product_info_node,
            'Product_Organisation/Granule_List/Granule')
        self.reflectance_conversion_node = get_xml_node(
            self._root,
            'n1:General_Info/Product_Image_Characteristics/Reflectance_Conversion'
        )
        self.qa_node = get_xml_node(self._root, 'n1:Quality_Indicators_Info')

        def _get_geometries():
            geometric_info = self._root.find('n1:Geometric_Info',
                                             self._root.nsmap)
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

        self.bbox, self.geometry = _get_geometries()

    @property
    def product_id(self) -> str:
        result = get_xml_node_text(self.product_info_node, 'PRODUCT_URI')
        if result is None:
            raise ValueError(
                'Cannot determine product ID using product metadata '
                f'at {self.href}')
        else:
            return result

    @property
    def datetime(self) -> datetime:
        time = get_xml_node_text(self.product_info_node, 'PRODUCT_START_TIME')
        if time is None:
            raise ValueError(
                'Cannot determine product start time using product metadata '
                f'at {self.href}')
        else:
            return str_to_datetime(time)

    @property
    def image_media_type(self) -> str:
        if get_xml_node_attr(self.granule_node, 'imageFormat') == 'GeoTIFF':
            return pystac.MediaType.COG
        else:
            return pystac.MediaType.JPEG2000

    @property
    def image_paths(self) -> List[str]:
        extension = '.tif' if self.image_media_type == pystac.MediaType.COG else '.jp2'

        return [
            f'{x.text}{extension}'
            for x in list_xml_node(self.granule_node, 'IMAGE_FILE')
        ]

    @property
    def relative_orbit(self) -> Optional[int]:
        return convert(
            int, get_xml_node_text(self.datatake_node, 'SENSING_ORBIT_NUMBER'))

    @property
    def orbit_state(self) -> Optional[str]:
        return get_xml_node_text(self.datatake_node, 'SENSING_ORBIT_DIRECTION')

    @property
    def platform(self) -> Optional[str]:
        return get_xml_node_text(self.datatake_node, 'SPACECRAFT_NAME')

    @property
    def mgrs_tile(self) -> Optional[str]:
        m = re.search(r'_T(\d{2}[a-zA-Z]{3})_', self.href)
        return None if m is None else m.group(1)

    @property
    def metadata_dict(self):
        result = {
            's2:product_uri':
            self.product_id,
            's2:generation_time':
            get_xml_node_text(self.product_info_node, 'GENERATION_TIME'),
            's2:processing_baseline':
            get_xml_node_text(self.product_info_node, 'PROCESSING_BASELINE'),
            's2:product_type':
            get_xml_node_text(self.product_info_node, 'PRODUCT_TYPE'),
            's2:datatake_id':
            get_xml_node_attr(self.datatake_node, 'datatakeIdentifier'),
            's2:datatake_type':
            get_xml_node_text(self.datatake_node, 'DATATAKE_TYPE'),
            's2:datastrip_id':
            get_xml_node_attr(self.granule_node, 'datastripIdentifier'),
            's2:granule_id':
            get_xml_node_attr(self.granule_node, 'granuleIdentifier'),
            's2:mgrs_tile':
            self.mgrs_tile,
            's2:reflectance_conversion_factor':
            convert(float,
                    get_xml_node_text(self.reflectance_conversion_node, 'U')),
            's2:cloud_coverage_assessment':
            convert(
                float,
                get_xml_node_text(self.qa_node, 'Cloud_Coverage_Assessment')),
            's2:degraded_msi_data_percentage':
            convert(
                float,
                get_xml_node_text(
                    self._root,
                    'n1:Quality_Indicators_Info/Technical_Quality_Assessment/'
                    + 'DEGRADED_MSI_DATA_PERCENTAGE')),
        }

        irradiance_nodes = list_xml_node(
            self.reflectance_conversion_node,
            'Solar_Irradiance_List/SOLAR_IRRADIANCE')

        def _solar_irradiance_from_node(node):
            band_name = band_index_to_name(int(node.get('bandId')))
            key = f's2:solarIrradiance{band_name}'
            value = float(node.text)
            return {key: value}

        for node in irradiance_nodes:
            result.update(_solar_irradiance_from_node(node))

        return result

    def create_asset(self):
        asset = pystac.Asset(href=self.href,
                             media_type=pystac.MediaType.XML,
                             roles=['metadata'])
        return (PRODUCT_METADATA_ASSET_KEY, asset)
