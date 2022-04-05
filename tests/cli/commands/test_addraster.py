from tempfile import TemporaryDirectory

import pystac
from pystac.utils import make_absolute_href
from stactools.core import move_all_assets
from stactools.cli.commands.addraster import create_addraster_command
from stactools.testing import CliTestCase
from .test_cases import TestCases
from .cli_test_utils import expected_json


def create_temp_catalog_copy(tmp_dir):
    col = TestCases.planet_disaster()
    col.normalize_hrefs(tmp_dir)
    col.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
    move_all_assets(col, copy=True)
    col.save()

    return col


class AddRasterTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_addraster_command]

    def test_add_raster_to_item(self):
        with TemporaryDirectory() as tmp_dir:
            catalog = create_temp_catalog_copy(tmp_dir)
            items = list(catalog.get_all_items())
            item_path = make_absolute_href(
                items[0].get_self_href(), catalog.get_self_href()
            )

            cmd = ["addraster", item_path]
            self.run_command(cmd)

            updated = pystac.read_file(catalog.get_self_href())
            item = list(updated.get_all_items())[0]
            asset = item.get_assets().get("analytic")
            assert asset is not None
            expected = expected_json("rasterbands.json")
            self.maxDiff = None
            for a, b in zip(expected, asset.to_dict().get("raster:bands")):
                self.assertDictEqual(a, b)
