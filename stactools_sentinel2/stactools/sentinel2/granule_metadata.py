from typing import Dict, List, Optional, Tuple

import pystac

from stactools.core.io import ReadHrefModifier
from stactools.core.io.xml import XmlElement
from stactools.sentinel2.constants import GRANULE_METADATA_ASSET_KEY
from stactools.sentinel2.utils import band_index_to_name, map_type


class GranuleMetadataError(Exception):
    pass

class GranuleMetadata:
    def __init__(self,
                 href,
                 read_href_modifier: Optional[ReadHrefModifier] = None):
        self.href = href

        self._root = XmlElement.from_file(href, read_href_modifier)

        geocoding_node = self._root.find('n1:Geometric_Info/Tile_Geocoding')
        if geocoding_node is None:
            raise GranuleMetadataError(
                f"Cannot find geocoding node in {self.href}"
            )
        self._geocoding_node = geocoding_node

        tile_angles_node = self._root.find('n1:Geometric_Info/Tile_Angles')
        if tile_angles_node is None:
            raise GranuleMetadataError(
                f"Cannot find tile angles node in {self.href}"
            )
        self._tile_angles_node = tile_angles_node

        self._viewing_angle_nodes = self._tile_angles_node.findall(
            'Mean_Viewing_Incidence_Angle_List/Mean_Viewing_Incidence_Angle'
        )

        self.resolution_to_shape: Dict[int, Tuple[int, int]] = {}
        for size_node in self._geocoding_node.findall("Size"):
            res = size_node.get_attr("resolution")
            if res is None:
                raise GranuleMetadataError('Size element does not have resolution.')
            nrows = map_type(int, size_node.find_text('NROWS'))
            if nrows is None:
                raise GranuleMetadataError(
                    f'Could not get rows from size for resolution {res}')
            ncols = map_type(int, size_node.find_text('NCOLS'))
            if ncols is None:
                raise GranuleMetadataError(
                    f'Could not get columns from size for resolution {res}')
            self.resolution_to_shape[int(res)] = (nrows, ncols)

    @property
    def epsg(self) -> Optional[int]:
        epsg_str = self._geocoding_node.find_text('HORIZONTAL_CS_CODE')
        if epsg_str is None:
            return None
        else:
            return int(epsg_str.split(':')[1])

    @property
    def proj_bbox(self) -> List[float]:
        """The bbox of the image in the CRS of the image data"""
        nrows, ncols = self.resolution_to_shape[10]
        geoposition = self._geocoding_node.find('Geoposition')
        if geoposition is None:
            raise GranuleMetadataError(
                f'Cannot find geoposition node in {self.href}'
            )
        ulx = map_type(float, geoposition.find_text('ULX'))
        if ulx is None:
            raise GranuleMetadataError('Could not get upper left X coordinate')
        uly = map_type(float, geoposition.find_text('ULY'))
        if uly is None:
            raise GranuleMetadataError('Could not get upper left Y coordinate')

        return [ulx, uly - (10 * nrows), ulx + (10 * ncols), uly]

    @property
    def cloudiness_percentage(self) -> Optional[float]:
        return map_type(
            float,
            self._root.find_text(
                'n1:Quality_Indicators_Info/Image_Content_QI/CLOUDY_PIXEL_PERCENTAGE'
            )
        )

    @property
    def mean_solar_zenith(self) -> Optional[float]:
        return map_type(
            float,
            self._tile_angles_node.find_text(
                'Mean_Sun_Angle/ZENITH_ANGLE'
            )
        )

    @property
    def mean_solar_azimuth(self) -> Optional[float]:
        return map_type(
            float,
            self._tile_angles_node.find_text(
                'Mean_Sun_Angle/AZIMUTH_ANGLE'
            )
        )

    @property
    def metadata_dict(self):
        result = {
            's2:mean_solar_zenith': self.mean_solar_zenith,
            's2:mean_solar_azimuth': self.mean_solar_azimuth
        }

        for node in self._viewing_angle_nodes:
            band_text = node.get_attr('bandId')
            if band_text is None:
                raise GranuleMetadataError(
                    f'Cannot find bandId in viewing angle node for {self.href}'
                )
            band_name = band_index_to_name(int(band_text))
            zenith_key = f's2:meanIncidenceZenithAngle{band_name}'
            azimuth_key = f's2:meanIncidenceAzimuthAngle{band_name}'
            result[zenith_key] = map_type(float, node.find('ZENITH_ANGLE').text)
            result[azimuth_key] = map_type(float,
                                          node.find('AZIMUTH_ANGLE').text)

        return result

    def create_asset(self):
        asset = pystac.Asset(href=self.href,
                             media_type=pystac.MediaType.XML,
                             roles=['metadata'])
        return (GRANULE_METADATA_ASSET_KEY, asset)
