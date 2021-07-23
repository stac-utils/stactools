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
        try:
            import s3fs  # noqa
        except ImportError:
            raise SkipTest(
                "Skipping testing external data with s3 because s3fs is not installed"
            )
        path = test_data.get_external_data("goes-16/index.html")
        with open(path) as f:
            html = f.read()
        self.assertNotEqual(
            html.find("Amazon"), -1,
            "Could not find 'Amazon' in the index page for the AWS public dataset"
        )
