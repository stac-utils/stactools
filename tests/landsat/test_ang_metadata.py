import unittest

from shapely.geometry import mapping, shape, box

from stactools.core.projection import reproject_geom
from stactools.landsat.ang_metadata import AngMetadata
from stactools.landsat.mtl_metadata import MtlMetadata

from tests.utils import TestData


class AngMetadataTest(unittest.TestCase):
    def test_parses(self):
        ang_path = TestData.get_path(
            'data-files/landsat/assets/LC08_L2SP_005009_20150710_20200908_02_T2_ANG.txt'
        )
        ang_path = TestData.get_path(
            'data-files/landsat/assets3/LC08_L2SP_008059_20191201_20200825_02_T1_ANG.txt'
        )

        ang_metadata = AngMetadata.from_file(ang_path)

        # self.assertEqual(ang_metadata.scene_id, "LC80050092015191LGN01")

        # Check that the proj_bbox from the MTL lines up with
        # the derived geometry.
        mtl_metadata = MtlMetadata.from_file(
            ang_path.replace('_ANG.txt', '_MTL.xml'))
        ang_geom = shape(ang_metadata.get_scene_geometry(mtl_metadata.bbox))
        proj_bbox = mtl_metadata.proj_bbox
        proj_bbox_shp = box(*proj_bbox)
        reproj_bbox_shp = shape(
            reproject_geom(f"epsg:{mtl_metadata.epsg}", "epsg:4326",
                           mapping(proj_bbox_shp)))
        ang_geom_shp = shape(ang_geom)

        self.assertLess((ang_geom_shp - reproj_bbox_shp).area,
                        0.0001 * ang_geom_shp.area)
