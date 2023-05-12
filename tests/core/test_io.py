import io
import os
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import create_autospec, patch

import pystac
import stactools.core.io
from stactools.core import use_fsspec


class IOTest(unittest.TestCase):
    def test_fsspec_io(self):
        use_fsspec()

        with TemporaryDirectory() as tmp_dir:
            catalog_url = (
                "https://raw.githubusercontent.com/stac-utils/pystac/v0.5.2/tests/data-files/"
                "catalogs/test-case-1/catalog.json"
            )

            cat = pystac.read_file(catalog_url)
            col = cat.get_child("country-1")
            self.assertEqual(len(list(col.get_children())), 2)

            cat.normalize_and_save(tmp_dir, pystac.CatalogType.SELF_CONTAINED)

            cat2 = pystac.read_file(os.path.join(tmp_dir, "catalog.json"))
            col2 = cat2.get_child("country-1")
            self.assertEqual(len(list(col2.get_children())), 2)

    @patch("stactools.core.io.fsspec.open")
    def test_fsspec_kwargs(self, mock_open):
        open_file = create_autospec(io.TextIOBase)
        open_file.read.return_value = "string"
        use_fsspec()
        url = "url"
        mock_open.return_value.__enter__.return_value = open_file
        stactools.core.io.read_text(url, requester_pays=True)
        mock_open.assert_called_with(url, "r", requester_pays=True)
