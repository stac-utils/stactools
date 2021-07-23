from unittest import TestCase, SkipTest

import pystac

from tests.testing import test_data


class TestDataTest(TestCase):
    """Say test ONE MORE TIME and I swear..."""
    def test_external_data_https(self):
        path = test_data.get_external_data("item.json")
        item = pystac.read_file(path)
        self.assertEqual(item.id, "20201211_223832_CS2")

    def test_external_data_s3(self):
        skip_without_s3fs()
        path = test_data.get_external_data("goes-16/index.html")
        with open(path) as f:
            html = f.read()
        self.assertNotEqual(
            html.find("Amazon"), -1,
            "Could not find 'Amazon' in the index page for the AWS public dataset"
        )

    def test_external_data_s3_with_config(self):
        skip_without_s3fs()
        path = test_data.get_external_data("AW3D30_global.vrt")
        with open(path) as f:
            xml = f.read()
        self.assertNotEqual(
            xml.find("ALPSMLC30_N041W106_DSM"), -1,
            "Could not find 'ALPSMLC30_N041W106_DSM' in the ALOS VRT")


def skip_without_s3fs():
    try:
        import s3fs  # noqa
    except ImportError:
        raise SkipTest(
            "Skipping testing external data with s3 because s3fs is not installed"
        )
