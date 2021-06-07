from datetime import datetime
from typing import Any, Dict, List, Optional

from pystac.utils import str_to_datetime
from pyproj import Geod

from stactools.core.utils import map_opt
from stactools.core.projection import transform_from_bbox
from stactools.core.io import ReadHrefModifier
from stactools.core.io.xml import XmlElement


class MTLError(Exception):
    pass


class MtlMetadata:
    """Parses a Collection 2 MTL XML file.

    References https://github.com/sat-utils/sat-stac-landsat/blob/f2263485043a827b4153aecc12f45a3d1363e9e2/satstac/landsat/main.py#L157
    """  # noqa

    def __init__(self, root: XmlElement, href: Optional[str] = None):
        self._root = root
        self.href = href

    def _xml_error(self, item: str) -> MTLError:
        return MTLError(f"Cannot find {item} in MTL metadata" +
                        ("" if self.href is None else f" at {self.href}"))

    def _get_text(self, xpath: str) -> str:
        return self._root.find_text_or_throw(xpath, self._xml_error)

    def _get_float(self, xpath: str) -> float:
        return float(self._get_text(xpath))

    def _get_int(self, xpath: str) -> int:
        return int(self._get_text(xpath))

    @property
    def scene_id(self) -> str:
        return self._get_text("PRODUCT_CONTENTS/LANDSAT_PRODUCT_ID")

    @property
    def processing_level(self) -> str:
        """Processing level. Determines product contents.

        Returns either 'L2SP' or 'L2SR', standing for
        'Level 2 Science Product' and 'Level 2 Surface Reflectance',
        respectively. L2SP has thermal + surface reflectance assets;
        L2SR only has surface reflectance.
        """
        return self._get_text("PRODUCT_CONTENTS/PROCESSING_LEVEL")

    @property
    def epsg(self) -> int:
        utm_zone = self._root.find_text('PROJECTION_ATTRIBUTES/UTM_ZONE')
        if utm_zone:
            bbox = self.bbox
            utm_zone = self._get_text('PROJECTION_ATTRIBUTES/UTM_ZONE')
            center_lat = (bbox[1] + bbox[3]) / 2.0
            return int(f"{326 if center_lat > 0 else 327}{utm_zone}")
        else:
            # Polar Stereographic
            # Based on Landsat 8-9 OLI/TIRS Collection 2 Level 1 Data Format Control Book,
            # should only ever be 71 or -71
            lat_ts = self._get_text('PROJECTION_ATTRIBUTES/TRUE_SCALE_LAT')
            if lat_ts == "-71.00000":
                # Antarctic
                return 3031
            elif lat_ts == "71.00000":
                # Arctic
                return 3995
            else:
                raise MTLError(
                    f'Unexpeced value for PROJECTION_ATTRIBUTES/TRUE_SCALE_LAT: {lat_ts} '
                )

    @property
    def bbox(self) -> List[float]:
        lons = [
            self._get_float("PROJECTION_ATTRIBUTES/CORNER_UL_LON_PRODUCT"),
            self._get_float("PROJECTION_ATTRIBUTES/CORNER_UR_LON_PRODUCT"),
            self._get_float("PROJECTION_ATTRIBUTES/CORNER_LL_LON_PRODUCT"),
            self._get_float("PROJECTION_ATTRIBUTES/CORNER_LR_LON_PRODUCT")
        ]

        lats = [
            self._get_float("PROJECTION_ATTRIBUTES/CORNER_UL_LAT_PRODUCT"),
            self._get_float("PROJECTION_ATTRIBUTES/CORNER_UR_LAT_PRODUCT"),
            self._get_float("PROJECTION_ATTRIBUTES/CORNER_LL_LAT_PRODUCT"),
            self._get_float("PROJECTION_ATTRIBUTES/CORNER_LR_LAT_PRODUCT")
        ]
        geod = Geod(ellps="WGS84")
        offset = self.sr_gsd / 2
        _, _, bottom_distance = geod.inv(lons[2], lats[2], lons[3], lats[3])
        bottom_offset = offset * (lons[3] - lons[2]) / bottom_distance
        _, _, top_distance = geod.inv(lons[0], lats[0], lons[1], lats[1])
        top_offset = offset * (lons[1] - lons[0]) / top_distance
        _, _, lat_distance = geod.inv(lons[0], lats[0], lons[2], lats[2])
        lat_offset = offset * (lats[0] - lats[2]) / lat_distance
        return [
            min(lons) - bottom_offset,
            min(lats) - lat_offset,
            max(lons) + top_offset,
            max(lats) + lat_offset
        ]

    @property
    def proj_bbox(self) -> List[float]:
        # USGS metadata provide bounds at the center of the pixel, but
        # GDAL/rasterio transforms are to edge of pixel.
        # https://github.com/stac-utils/stactools/issues/117
        offset = self.sr_gsd / 2
        xs = [
            self._get_float(
                "PROJECTION_ATTRIBUTES/CORNER_UL_PROJECTION_X_PRODUCT") -
            offset,
            self._get_float(
                "PROJECTION_ATTRIBUTES/CORNER_UR_PROJECTION_X_PRODUCT") +
            offset,
            self._get_float(
                "PROJECTION_ATTRIBUTES/CORNER_LL_PROJECTION_X_PRODUCT") -
            offset,
            self._get_float(
                "PROJECTION_ATTRIBUTES/CORNER_LR_PROJECTION_X_PRODUCT") +
            offset
        ]

        ys = [
            self._get_float(
                "PROJECTION_ATTRIBUTES/CORNER_UL_PROJECTION_Y_PRODUCT") +
            offset,
            self._get_float(
                "PROJECTION_ATTRIBUTES/CORNER_UR_PROJECTION_Y_PRODUCT") +
            offset,
            self._get_float(
                "PROJECTION_ATTRIBUTES/CORNER_LL_PROJECTION_Y_PRODUCT") -
            offset,
            self._get_float(
                "PROJECTION_ATTRIBUTES/CORNER_LR_PROJECTION_Y_PRODUCT") -
            offset
        ]

        return [min(xs), min(ys), max(xs), max(ys)]

    @property
    def sr_shape(self) -> List[int]:
        """Shape for surface reflectance assets.

        Used for proj:shape. In [row, col] order"""
        return [
            self._get_int("PROJECTION_ATTRIBUTES/REFLECTIVE_LINES"),
            self._get_int("PROJECTION_ATTRIBUTES/REFLECTIVE_SAMPLES")
        ]

    @property
    def thermal_shape(self) -> Optional[List[int]]:
        """Shape for thermal bands (Bands 10–11).

        None if thermal bands not present.
        Used for proj:shape. In [row, col] order"""
        rows = map_opt(
            int, self._root.find_text("PROJECTION_ATTRIBUTES/THERMAL_LINES"))
        cols = map_opt(
            int, self._root.find_text("PROJECTION_ATTRIBUTES/THERMAL_SAMPLES"))

        if rows is not None and cols is not None:
            return [rows, cols]
        else:
            return None

    @property
    def sr_transform(self) -> List[float]:
        return transform_from_bbox(self.proj_bbox, self.sr_shape)

    @property
    def thermal_transform(self) -> Optional[List[float]]:
        return map_opt(
            lambda shape: transform_from_bbox(self.proj_bbox, shape),
            self.thermal_shape)

    @property
    def sr_gsd(self) -> float:
        return self._get_float(
            "LEVEL1_PROJECTION_PARAMETERS/GRID_CELL_SIZE_THERMAL")

    @property
    def thermal_gsd(self) -> Optional[float]:
        return map_opt(
            float,
            self._root.find_text(
                'LEVEL1_PROJECTION_PARAMETERS/GRID_CELL_SIZE_THERMAL'))

    @property
    def scene_datetime(self) -> datetime:
        date = self._get_text("IMAGE_ATTRIBUTES/DATE_ACQUIRED")
        time = self._get_text("IMAGE_ATTRIBUTES/SCENE_CENTER_TIME")

        return str_to_datetime(f"{date} {time}")

    @property
    def cloud_cover(self) -> float:
        return self._get_float("IMAGE_ATTRIBUTES/CLOUD_COVER")

    @property
    def sun_azimuth(self) -> float:
        return self._get_float("IMAGE_ATTRIBUTES/SUN_AZIMUTH")

    @property
    def sun_elevation(self) -> float:
        return self._get_float("IMAGE_ATTRIBUTES/SUN_ELEVATION")

    @property
    def off_nadir(self) -> Optional[float]:
        if self._get_text("IMAGE_ATTRIBUTES/NADIR_OFFNADIR") == "NADIR":
            return 0
        else:
            return None

    @property
    def wrs_path(self) -> str:
        return self._get_text("IMAGE_ATTRIBUTES/WRS_PATH").zfill(3)

    @property
    def wrs_row(self) -> str:
        return self._get_text("IMAGE_ATTRIBUTES/WRS_ROW").zfill(3)

    @property
    def additional_metadata(self) -> Dict[str, Any]:
        return {
            "landsat:cloud_cover_land":
            self._get_float("IMAGE_ATTRIBUTES/CLOUD_COVER_LAND"),
            "landsat:wrs_type":
            self._get_text("IMAGE_ATTRIBUTES/WRS_TYPE"),
            "landsat:wrs_path":
            self.wrs_path,
            "landsat:wrs_row":
            self.wrs_row,
            "landsat:collection_category":
            self._get_text("PRODUCT_CONTENTS/COLLECTION_CATEGORY"),
            "landsat:collection_number":
            self._get_text("PRODUCT_CONTENTS/COLLECTION_NUMBER"),
            "landsat:processing_level":
            self.processing_level
        }

    @classmethod
    def from_file(cls,
                  href,
                  read_href_modifier: Optional[ReadHrefModifier] = None
                  ) -> "MtlMetadata":
        return cls(XmlElement.from_file(href, read_href_modifier), href=href)
