import unittest

from shapely.geometry import mapping, shape, box

from stactools.core.projection import reproject_geom
from stactools.landsat.mtl_metadata import MtlMetadata

from tests.utils import TestData


class MtlMetadataTest(unittest.TestCase):
    def test_parses_xml_utm(self):
        mtl_path = TestData.get_path(
            'data-files/landsat/assets/LC08_L2SP_005009_20150710_20200908_02_T2_MTL.xml'
        )

        mtl_metadata = MtlMetadata.from_file(mtl_path)

        # Datetime
        dt = mtl_metadata.scene_datetime
        self.assertEqual(dt.month, 7)
        self.assertEqual(dt.minute, 34)

        # epsg
        epsg = mtl_metadata.epsg
        self.assertEqual(epsg, 32624)

        # bboxes
        bbox = mtl_metadata.bbox
        bbox_shp = box(*bbox)
        proj_bbox = mtl_metadata.proj_bbox
        proj_bbox_shp = box(*proj_bbox)
        reproj_bbox_shp = shape(
            reproject_geom(f"epsg:{epsg}", "epsg:4326",
                           mapping(proj_bbox_shp)))

        self.assertLess((reproj_bbox_shp - bbox_shp).area,
                        0.0001 * reproj_bbox_shp.area)

        # Cloud Cover
        cloud_cover = mtl_metadata.cloud_cover
        self.assertEqual(cloud_cover, 54.65)

        # View
        off_nadir = mtl_metadata.off_nadir
        self.assertEqual(off_nadir, 0.0)

        sun_azimuth = mtl_metadata.sun_azimuth
        self.assertEqual(sun_azimuth, 177.8846007)

        sun_elevation = mtl_metadata.sun_elevation
        self.assertEqual(sun_elevation, 40.0015903)

    def test_parses_xml_ps(self):
        mtl_path = TestData.get_path(
            'data-files/landsat/assets2/LC08_L2SR_099120_20191129_20201016_02_T2_MTL.xml'
        )
        mtl_metadata = MtlMetadata.from_file(mtl_path)

        # epsg
        epsg = mtl_metadata.epsg
        self.assertEqual(epsg, 3031)

        # bboxes
        bbox = mtl_metadata.bbox
        bbox_shp = box(*bbox)
        proj_bbox = mtl_metadata.proj_bbox
        proj_bbox_shp = box(*proj_bbox)
        reproj_bbox_shp = shape(
            reproject_geom(f"epsg:{epsg}", "epsg:4326",
                           mapping(proj_bbox_shp)))

        self.assertLess((reproj_bbox_shp - bbox_shp).area,
                        0.0001 * reproj_bbox_shp.area)
