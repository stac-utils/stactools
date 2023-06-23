from tempfile import TemporaryDirectory

import pystac
from pystac.utils import make_absolute_href
from stactools.cli.commands.add_raster import create_add_raster_command
from stactools.testing import CliTestCase

from tests.utils import create_planet_disaster_clone

from .cli_test_utils import expected_json


class AddRasterTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_add_raster_command]

    def test_add_raster_to_item(self):
        with TemporaryDirectory() as tmp_dir:
            catalog = create_planet_disaster_clone(tmp_dir)
            items = list(catalog.get_all_items())
            item_path = make_absolute_href(
                items[0].get_self_href(), catalog.get_self_href()
            )

            cmd = ["add-raster", item_path]
            self.run_command(cmd)

            updated = pystac.read_file(catalog.get_self_href())
            item = list(updated.get_all_items())[0]
            asset = item.get_assets().get("analytic")
            assert asset is not None
            expected = expected_json("rasterbands.json")
            self.maxDiff = None
            for a, b in zip(expected, asset.to_dict().get("raster:bands")):
                self.assertDictEqual(a, b)
