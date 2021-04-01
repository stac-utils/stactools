import logging
from typing import Any, Dict, List, Optional

from stactools.core.io import ReadHrefModifier, read_text

logger = logging.getLogger(__name__)


class AngError(Exception):
    pass


class AngMetadata:
    """Represents the Angle Coefficient file (ANG) file.

    The ANG file can be used to derive the scene geometry.

    Modified from https://github.com/sat-utils/sat-stac-landsat/blob/485eb6874cf0e20744a19970c6d8a295eee5942d/satstac/landsat/main.py#L108
    """  # noqa

    def __init__(self, ang_txt: str, href: Optional[str] = None):
        self._sz = []
        self._coords = []
        scene_id = None

        try:
            for line in ang_txt.split('\n'):
                if 'LANDSAT_SCENE_ID' in line:
                    scene_id = line.split('=')[1].strip(' "')
                if 'BAND01_NUM_L1T_LINES' in line or 'BAND01_NUM_L1T_SAMPS' in line:
                    self._sz.append(float(line.split('=')[1]))
                if ('BAND01_L1T_IMAGE_CORNER_LINES' in line
                        or 'BAND01_L1T_IMAGE_CORNER_SAMPS' in line):
                    self._coords.append([
                        float(x) for x in line.split('=')[1].strip().strip(
                            '()').split(',')
                    ])
                if len(self._coords) == 2:
                    break
        except Exception as e:
            href_msg = "" if href is None else f" from {href}"
            raise AngError(f"Could not parse ANG file{href_msg}") from e

        if scene_id is None:
            href_msg = "" if href is None else f" from {href}"
            raise AngError(f"Could not get scene id {href_msg}")

        self.scene_id = scene_id

    def get_scene_geometry(self, bbox: List[float]) -> Dict[str, Any]:
        """Get the scene geometry from the ANG file based on the
        bbox supplied by the MTL.

        TODO: This produces a footprint that is larger than the ones provided
        by the USGS STAC Items. Determine how to more closely match USGS, or
        get them to publish the footprint geom as an additional product file.
        """
        dlon = bbox[2] - bbox[0]
        dlat = bbox[3] - bbox[1]
        lons = [c / self._sz[1] * dlon + bbox[0] for c in self._coords[1]]
        lats = [((self._sz[0] - c) / self._sz[0]) * dlat + bbox[1]
                for c in self._coords[0]]
        coordinates = [[[lons[0], lats[0]], [lons[1], lats[1]],
                        [lons[2], lats[2]], [lons[3], lats[3]],
                        [lons[0], lats[0]]]]
        return {'type': 'Polygon', 'coordinates': coordinates}

    @classmethod
    def from_file(cls,
                  href,
                  read_href_modifier: Optional[ReadHrefModifier] = None
                  ) -> "AngMetadata":
        return cls(read_text(href, read_href_modifier), href=href)
