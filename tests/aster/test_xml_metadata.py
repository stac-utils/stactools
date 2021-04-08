import unittest

from shapely.geometry import shape, box

from stactools.aster.xml_metadata import XmlMetadata
from stactools.aster.constants import (SWIR_SENSOR, TIR_SENSOR,
                                       UPPER_LEFT_QUAD_CLOUD_COVER,
                                       UPPER_RIGHT_QUAD_CLOUD_COVER,
                                       LOWER_LEFT_QUAD_CLOUD_COVER,
                                       LOWER_RIGHT_QUAD_CLOUD_COVER,
                                       VNIR_SENSOR)
from tests.utils import TestData


class XmlMetadataTest(unittest.TestCase):
    def test_parses_xml(self):
        xml_path = TestData.get_path(
            'data-files/aster/AST_L1T_00305032000040446_20150409135350_78838.hdf.xml'
        )
        xml_metadata = XmlMetadata.from_file(xml_path)

        # Geometries
        geom, bbox = xml_metadata.geometries
        geom_shp = shape(geom)
        self.assertGreater(geom_shp.area, 0.0)
        bbox_shp = box(*bbox)
        self.assertGreater(bbox_shp.area, 0.0)
        self.assertTrue(bbox_shp.covers(geom_shp))

        # Datetime
        dt = xml_metadata.item_datetime
        self.assertEqual(dt.day, 3)
        self.assertEqual(dt.second, 46)

        # Cloud Cover
        cloud_cover = xml_metadata.cloud_cover
        self.assertEqual(cloud_cover, 57)

        # Pointing angles
        pointing_angles = xml_metadata.pointing_angles
        self.assertEqual(len(pointing_angles.keys()), 3)
        self.assertEqual(pointing_angles[VNIR_SENSOR], 5.721)
        self.assertEqual(pointing_angles[SWIR_SENSOR], 5.680)
        self.assertEqual(pointing_angles[TIR_SENSOR], 5.709)

        # UTM Zone
        utm_zone = xml_metadata.utm_zone
        self.assertEqual(utm_zone, 48)

        # ASTER properties
        aster_properties = xml_metadata.aster_properties
        self.assertEqual(aster_properties[UPPER_LEFT_QUAD_CLOUD_COVER], 64.0)
        self.assertEqual(aster_properties[UPPER_RIGHT_QUAD_CLOUD_COVER], 44.0)
        self.assertEqual(aster_properties[LOWER_LEFT_QUAD_CLOUD_COVER], 75.0)
        self.assertEqual(aster_properties[LOWER_RIGHT_QUAD_CLOUD_COVER], 44.0)
