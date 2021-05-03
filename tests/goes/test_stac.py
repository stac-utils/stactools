import dateutil
import os.path
from tempfile import TemporaryDirectory
import unittest

from pystac import MediaType
from pystac.extensions.projection import ProjectionExtension

from stactools.goes import stac
from tests.utils import TestData

EXTERNAL_DATA_PATH = (
    "goes/OR_ABI-L2-CMIPM1-M6C02_G16_s20211231619248_e20211231619306_c20211231619382.nc"
)


class CreateItemTest(unittest.TestCase):
    def test_create_item(self):
        path = TestData.get_external_data(EXTERNAL_DATA_PATH)
        item = stac.create_item(path)
        self.assertEqual(
            item.id,
            "OR_ABI-L2-CMIPM1-M6C02_G16_s20211231619248_e20211231619306_c20211231619382"
        )
        self.assertTrue(item.geometry)
        self.assertTrue(item.bbox)
        self.assertEqual(item.datetime,
                         dateutil.parser.parse("2021-05-03T16:19:38.2Z"))
        self.assertEqual(item.common_metadata.start_datetime,
                         dateutil.parser.parse("2021-05-03T16:19:24.8Z"))
        self.assertEqual(item.common_metadata.end_datetime,
                         dateutil.parser.parse("2021-05-03T16:19:30.6Z"))

        data = item.assets["data"]
        self.assertEqual(data.href, path)
        self.assertEqual(data.title, "ABI L2 Cloud and Moisture Imagery")
        self.assertEqual(data.media_type, "application/netcdf")
        self.assertEqual(data.roles, ["data"])

        projection = ProjectionExtension.ext(item)
        self.assertIsNone(projection.epsg)
        self.assertIsNotNone(projection.wkt2)
        self.assertIsNotNone(projection.shape, [2000, 2000])
        expected_transform = [
            501.0043288718852, 0.0, -2224459.203445637, 0.0,
            -501.0043288718852, 4068155.14931683, 0.0, 0.0, 1.0
        ]
        for actual, expected in zip(projection.transform, expected_transform):
            self.assertAlmostEqual(actual, expected, delta=1e-4)

        item.validate()

    def test_read_href_modifier(self):
        did_it = False

        def modify_href(href: str) -> str:
            nonlocal did_it
            did_it = True
            return href

        path = TestData.get_external_data(EXTERNAL_DATA_PATH)
        _ = stac.create_item(path, modify_href)
        self.assertTrue(did_it)

    def test_cog_directory(self):
        path = TestData.get_external_data(EXTERNAL_DATA_PATH)
        with TemporaryDirectory() as tmp_dir:
            item = stac.create_item(path, cog_directory=tmp_dir)
            cog_asset = item.assets["CMI"]
            self.assertTrue(os.path.exists(cog_asset.href))
            self.assertEqual(
                cog_asset.title,
                "ABI L2 Cloud and Moisture Imagery Cloud Optimized Geotiff (CMI)"
            )
            self.assertEqual(cog_asset.roles, ["data"])
            self.assertEqual(cog_asset.media_type, MediaType.COG)

    def test_different_product(self):
        path = TestData.get_path(
            "data-files/goes/"
            "OR_ABI-L2-LSTM2-M6_G16_s20211381700538_e20211381700595_c20211381701211.nc"
        )
        item = stac.create_item(path)
        item.validate()
