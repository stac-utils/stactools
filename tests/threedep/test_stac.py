import datetime
import unittest

from tests.utils import TestData
from stactools.threedep import stac
from stactools.threedep.constants import USGS_FTP_BASE


class CreateItemTest(unittest.TestCase):
    def test_create_item_1(self):
        path = TestData.get_path(
            "data-files/threedep/base/1/TIFF/n41w106/USGS_1_n41w106.xml")
        item = stac.create_item(path)
        self.assertEqual(item.id, "n41w106-1")
        self.assertTrue(item.geometry is not None)
        self.assertTrue(item.bbox is not None)
        self.assertEqual(
            item.datetime,
            datetime.datetime(2015,
                              7,
                              17,
                              0,
                              0,
                              0,
                              tzinfo=datetime.timezone.utc))
        self.assertEqual(
            item.common_metadata.start_datetime,
            datetime.datetime(1948,
                              1,
                              1,
                              0,
                              0,
                              0,
                              tzinfo=datetime.timezone.utc))
        self.assertEqual(
            item.common_metadata.end_datetime,
            datetime.datetime(2013,
                              12,
                              31,
                              0,
                              0,
                              0,
                              tzinfo=datetime.timezone.utc))
        self.assertEqual(item.common_metadata.gsd, 30)

        data = item.assets["data"]
        self.assertEqual(data.href,
                         ("https://prd-tnm.s3.amazonaws.com/StagedProducts"
                          "/Elevation/1/TIFF/n41w106/USGS_1_n41w106.tif"))
        self.assertEqual(data.title, "USGS 1 arc-second n41w106 1 x 1 degree")
        self.assertTrue(
            data.description.startswith(
                "This tile of the 3D Elevation Program (3DEP)"))
        self.assertTrue(
            data.media_type,
            "image/tiff; application=geotiff; profile=cloud-optimized")
        self.assertTrue(data.roles, ["data"])

        data = item.assets["metadata"]
        self.assertEqual(data.href,
                         ("https://prd-tnm.s3.amazonaws.com/StagedProducts"
                          "/Elevation/1/TIFF/n41w106/USGS_1_n41w106.xml"))
        self.assertTrue(data.title is None)
        self.assertTrue(data.description is None)
        self.assertEqual(data.media_type, "application/xml")
        self.assertEqual(data.roles, ["metadata"])

        data = item.assets["thumbnail"]
        self.assertEqual(
            data.href,
            ("https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/"
             "1/TIFF/n41w106/USGS_1_n41w106.jpg"))
        self.assertTrue(data.title is None)
        self.assertTrue(data.description is None)
        self.assertEqual(data.media_type, "image/jpeg")
        self.assertEqual(data.roles, ["thumbnail"])

        link = next(link for link in item.links if link.rel == "via")
        self.assertTrue(link is not None)
        self.assertEqual(link.target,
                         ("https://prd-tnm.s3.amazonaws.com/StagedProducts"
                          "/Elevation/1/TIFF/n41w106/USGS_1_n41w106.xml"))

        item.ext.enable("projection")
        self.assertEqual(item.ext.projection.epsg, 5498)
        self.assertEqual(item.ext.projection.shape, [3612, 3612])
        self.assertEqual(item.ext.projection.transform, [
            0.00027777778, 0.0, -106.001666667082, 0.0, -0.00027777778,
            41.0016666667842, 0.0, 0.0, 1.0
        ])

        item.validate()

    def test_create_item_1_weird_date(self):
        path = TestData.get_path(
            "data-files/threedep/one-offs/USGS_1_n19w090.xml")
        item = stac.create_item(path)
        self.assertEqual(
            item.datetime,
            datetime.datetime(2013,
                              1,
                              1,
                              0,
                              0,
                              0,
                              tzinfo=datetime.timezone.utc))

    def test_create_item_13(self):
        path = TestData.get_path(
            "data-files/threedep/base/13/TIFF/n41w106/USGS_13_n41w106.xml")
        item = stac.create_item(path)
        self.assertEqual(item.id, "n41w106-13")
        self.assertEqual(item.common_metadata.gsd, 10)

    def test_create_item_with_base(self):
        path = TestData.get_path(
            "data-files/threedep/base/1/TIFF/n41w106/USGS_1_n41w106.xml")
        item = stac.create_item(path, base=USGS_FTP_BASE)
        data = item.assets["data"]
        self.assertEqual(
            data.href, ("ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged"
                        "/Elevation/1/TIFF/n41w106/USGS_1_n41w106.tif"))
        data = item.assets["metadata"]
        self.assertEqual(
            data.href, ("ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged"
                        "/Elevation/1/TIFF/n41w106/USGS_1_n41w106.xml"))
        data = item.assets["thumbnail"]
        self.assertEqual(
            data.href,
            ("ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Elevation/"
             "1/TIFF/n41w106/USGS_1_n41w106.jpg"))
        link = next(link for link in item.links if link.rel == "via")
        self.assertTrue(link is not None)
        self.assertEqual(
            link.target,
            ("ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged"
             "/Elevation/1/TIFF/n41w106/USGS_1_n41w106.xml"))

    def test_create_item_from_product_and_id(self):
        path = TestData.get_path("data-files/threedep/base")
        item = stac.create_item_from_product_and_id("1", "n41w106", path)
        item.validate()

    def test_read_href_modifier(self):
        did_it = False

        def modify_href(href: str) -> str:
            nonlocal did_it
            did_it = True
            return href

        path = TestData.get_path(
            "data-files/threedep/base/1/TIFF/n41w106/USGS_1_n41w106.xml")
        _ = stac.create_item(path, modify_href)
        self.assertTrue(did_it)

    def test_explicit_none_goes_to_aws(self):
        path = TestData.get_path(
            "data-files/threedep/base/1/TIFF/n41w106/USGS_1_n41w106.xml")
        item0 = stac.create_item(path)
        item1 = stac.create_item(path, base=None)
        self.assertEqual(item0.to_dict(), item1.to_dict())
