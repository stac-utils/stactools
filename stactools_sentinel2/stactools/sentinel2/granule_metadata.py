from typing import Dict, List, Optional, Tuple

import pystac

from stactools.sentinel2.constants import GRANULE_METADATA_ASSET_KEY
from stactools.sentinel2.utils import (ReadHrefModifier, band_index_to_name,
                                       get_xml_node, get_xml_node_text,
                                       list_xml_node, read_xml, convert,
                                       get_xml_node_attr)


class GranuleMetadata:
    def __init__(self,
                 href,
                 read_href_modifier: Optional[ReadHrefModifier] = None):
        self.href = href

        self._root = read_xml(href, read_href_modifier)

        self._geocoding_node = get_xml_node(
            self._root, 'n1:Geometric_Info/Tile_Geocoding')
        self._tile_angles_node = get_xml_node(self._root,
                                              'n1:Geometric_Info/Tile_Angles')
        self._viewing_angle_nodes = list_xml_node(
            self._tile_angles_node,
            'Mean_Viewing_Incidence_Angle_List/Mean_Viewing_Incidence_Angle')

        self.resolution_to_shape: Dict[int, Tuple[int, int]] = {}
        for size_node in list_xml_node(self._geocoding_node, "Size"):
            res = get_xml_node_attr(size_node, "resolution")
            if res is None:
                raise ValueError('Size element does not have resolution.')
            nrows = convert(int, get_xml_node_text(size_node, 'NROWS'))
            if nrows is None:
                raise ValueError(
                    f'Could not get rows from size for resolution {res}')
            ncols = convert(int, get_xml_node_text(size_node, 'NCOLS'))
            if ncols is None:
                raise ValueError(
                    f'Could not get columns from size for resolution {res}')
            self.resolution_to_shape[int(res)] = (nrows, ncols)

    @property
    def epsg(self) -> Optional[int]:
        epsg_str = get_xml_node_text(self._geocoding_node,
                                     'HORIZONTAL_CS_CODE')
        if epsg_str is None:
            return None
        else:
            return int(epsg_str.split(':')[1])

    @property
    def proj_bbox(self) -> List[float]:
        """The bbox of the image in the CRS of the image data"""
        nrows, ncols = self.resolution_to_shape[10]
        geoposition = get_xml_node(self._geocoding_node, 'Geoposition')
        ulx = convert(float, get_xml_node_text(geoposition, 'ULX'))
        if ulx is None:
            raise ValueError('Could not get upper left X coordinate')
        uly = convert(float, get_xml_node_text(geoposition, 'ULY'))
        if uly is None:
            raise ValueError('Could not get upper left Y coordinate')

        return [ulx, uly - (10 * nrows), ulx + (10 * ncols), uly]

    @property
    def cloudiness_percentage(self) -> Optional[float]:
        return convert(
            float,
            get_xml_node_text(
                self._root,
                'n1:Quality_Indicators_Info/Image_Content_QI/CLOUDY_PIXEL_PERCENTAGE'
            ))

    @property
    def mean_solar_zenith(self) -> Optional[float]:
        return convert(
            float,
            get_xml_node_text(self._tile_angles_node,
                              'Mean_Sun_Angle/ZENITH_ANGLE'))

    @property
    def mean_solar_azimuth(self) -> Optional[float]:
        return convert(
            float,
            get_xml_node_text(self._tile_angles_node,
                              'Mean_Sun_Angle/AZIMUTH_ANGLE'))

    @property
    def metadata_dict(self):
        result = {
            's2:mean_solar_zenith': self.mean_solar_zenith,
            's2:mean_solar_azimuth': self.mean_solar_azimuth
        }

        for node in self._viewing_angle_nodes:
            band_name = band_index_to_name(int(node.get('bandId')))
            zenith_key = f's2:meanIncidenceZenithAngle{band_name}'
            azimuth_key = f's2:meanIncidenceAzimuthAngle{band_name}'
            result[zenith_key] = convert(float, node.find('ZENITH_ANGLE').text)
            result[azimuth_key] = convert(float,
                                          node.find('AZIMUTH_ANGLE').text)

        return result

    def create_asset(self):
        asset = pystac.Asset(href=self.href,
                             media_type=pystac.MediaType.XML,
                             roles=['metadata'])
        return (GRANULE_METADATA_ASSET_KEY, asset)
