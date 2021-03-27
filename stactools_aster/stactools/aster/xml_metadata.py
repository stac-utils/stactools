from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pystac.extensions.sat import OrbitState
from pystac.utils import str_to_datetime
from shapely.geometry import Point, Polygon, mapping

from stactools.core.io import ReadHrefModifier
from stactools.core.io.xml import XmlElement
from stactools.core.utils import map_opt
from stactools.aster.constants import (LOWER_LEFT_QUAD_CLOUD_COVER,
                                       LOWER_RIGHT_QUAD_CLOUD_COVER,
                                       SWIR_SENSOR, TIR_SENSOR,
                                       UPPER_LEFT_QUAD_CLOUD_COVER,
                                       UPPER_RIGHT_QUAD_CLOUD_COVER,
                                       VNIR_SENSOR)
from stactools.aster.utils import epsg_from_aster_utm_zone_number


class XmlMetadataError(Exception):
    pass


class XmlMetadata:
    def __init__(self, root: XmlElement, href: Optional[str] = None):
        self.root = root
        self.href = href

        psas = root.findall("GranuleURMetaData/PSAs/PSA")
        if len(psas) == 0:
            raise self._xml_error("PSA data")
        self._psas = psas

    def _xml_error(self, item: str) -> XmlMetadataError:
        return XmlMetadataError(f"Cannot find {item} in metadata" + (
            "" if self.href is None else f" at {self.href}"))

    def _get_psa_value(self, name: str) -> str:
        result = next(
            iter([
                psa.find_text('PSAValue') for psa in self._psas
                if psa.find_text('PSAName') == name
            ]), None)
        if result is None:
            raise self._xml_error(name)
        return result

    @property
    def geometries(self) -> Tuple[Dict[str, Any], List[float]]:
        boundary_node = self.root.find(
            'GranuleURMetaData/SpatialDomainContainer'
            '/HorizontalSpatialDomainContainer/GPolygon/Boundary')
        if boundary_node is None:
            raise self._xml_error("spatial domain boundary node")

        poly_points = []
        for point_node in boundary_node.findall('Point'):
            lon = point_node.find_text('PointLongitude')
            if lon is None:
                raise self._xml_error("geom PointLongitude")
            lat = point_node.find_text('PointLatitude')
            if lat is None:
                raise self._xml_error("geom PointLatitude")
            poly_points.append(Point(float(lon), float(lat)))
        geom_shp = Polygon(poly_points)
        geom = mapping(geom_shp)
        bbox = list(geom_shp.bounds)

        return geom, bbox

    @property
    def item_datetime(self) -> datetime:
        tod_xpath = 'GranuleURMetaData/SingleDateTime/TimeofDay'
        date_xpath = 'GranuleURMetaData/SingleDateTime/CalendarDate'

        tod = self.root.find_text(tod_xpath)
        if tod is None:
            raise self._xml_error(tod_xpath)

        date = self.root.find_text(date_xpath)
        if date is None:
            raise self._xml_error(date_xpath)

        return str_to_datetime(f'{date}T{tod}Z')

    @property
    def created(self) -> Optional[datetime]:
        return map_opt(str_to_datetime,
                       self.root.find_text('GranuleURMetaData/InsertTime'))

    @property
    def updated(self) -> Optional[datetime]:
        return map_opt(str_to_datetime,
                       self.root.find_text('GranuleURMetaData/LastUpdate'))

    @property
    def cloud_cover(self) -> float:
        return float(self._get_psa_value('SceneCloudCoverage'))

    @property
    def pointing_angles(self) -> Dict[str, float]:
        return {
            VNIR_SENSOR: float(self._get_psa_value('ASTERVNIRPointingAngle')),
            SWIR_SENSOR: float(self._get_psa_value('ASTERSWIRPointingAngle')),
            TIR_SENSOR: float(self._get_psa_value('ASTERTIRPointingAngle'))
        }

    @property
    def sun_azimuth(self) -> float:
        return float(self._get_psa_value('Solar_Azimuth_Angle'))

    @property
    def sun_elevation(self) -> float:
        return float(self._get_psa_value('Solar_Elevation_Angle'))

    @property
    def utm_zone(self) -> int:
        return int(self._get_psa_value('UTMZoneNumber'))

    @property
    def epsg(self) -> int:
        return epsg_from_aster_utm_zone_number(self.utm_zone)

    @property
    def orbit_state(self) -> OrbitState:
        if self._get_psa_value('FlyingDirection') == 'DE':
            return OrbitState.DESCENDING
        else:
            return OrbitState.ASCENDING

    @property
    def aster_properties(self) -> Dict[str, Any]:
        result = {
            UPPER_LEFT_QUAD_CLOUD_COVER:
            float(self._get_psa_value('UpperLeftQuadCloudCoverage')),
            UPPER_RIGHT_QUAD_CLOUD_COVER:
            float(self._get_psa_value('UpperRightQuadCloudCoverage')),
            LOWER_LEFT_QUAD_CLOUD_COVER:
            float(self._get_psa_value('LowerLeftQuadCloudCoverage')),
            LOWER_RIGHT_QUAD_CLOUD_COVER:
            float(self._get_psa_value('LowerRightQuadCloudCoverage'))
        }

        return result

    @classmethod
    def from_file(cls,
                  href: str,
                  read_href_modifier: Optional[ReadHrefModifier] = None
                  ) -> "XmlMetadata":
        return cls(XmlElement.from_file(href,
                                        read_href_modifier=read_href_modifier),
                   href=href)
