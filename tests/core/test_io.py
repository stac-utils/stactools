import os
import unittest
from tempfile import TemporaryDirectory

import pystac
from stactools.core import use_fsspec


class IOTest(unittest.TestCase):

    def test_fsspec_io(self):
        use_fsspec()

        with TemporaryDirectory() as tmp_dir:
            catalog_url = (
                'https://raw.githubusercontent.com/stac-utils/pystac/v0.5.2/tests/data-files/'
                'catalogs/test-case-1/catalog.json')

            cat = pystac.read_file(catalog_url)
            col = cat.get_child('country-1')
            self.assertEqual(len(list(col.get_children())), 2)

            cat.normalize_and_save(tmp_dir, pystac.CatalogType.SELF_CONTAINED)

            cat2 = pystac.read_file(os.path.join(tmp_dir, 'catalog.json'))
            col2 = cat2.get_child('country-1')
            self.assertEqual(len(list(col2.get_children())), 2)
