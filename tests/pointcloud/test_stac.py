import datetime
import unittest

from tests.utils import TestData
from stactools.pointcloud.stac import create_item


class StacTest(unittest.TestCase):
    def test_create_item(self):
        path = TestData.get_path("data-files/pointcloud/autzen_trim.las")
        item = create_item(path)
        self.assertEqual(item.id, "autzen_trim")
        self.assertEqual(item.datetime, datetime.datetime(2015, 9, 10))

        item.ext.enable("projection")
        self.assertEqual(item.ext.projection.epsg, 2994)

        item.ext.enable("pointcloud")
        self.assertEqual(item.ext.pointcloud.count, 110000)
        self.assertEqual(item.ext.pointcloud.type, "lidar")
        self.assertEqual(item.ext.pointcloud.encoding, "las")
        self.assertEqual(item.ext.pointcloud.statistics, None)
        self.assertTrue(item.ext.pointcloud.schemas)

        item.validate()

    def test_create_item_with_statistic(self):
        path = TestData.get_path("data-files/pointcloud/autzen_trim.las")
        item = create_item(path, compute_statistics=True)
        self.assertNotEqual(item.ext.pointcloud.statistics, None)

    def test_create_item_from_url(self):
        url = "https://github.com/PDAL/PDAL/raw/2.2.0/test/data/las/autzen_trim.las"
        item = create_item(url)
        item.validate()
