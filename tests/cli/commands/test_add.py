from tempfile import TemporaryDirectory

import pystac
from stactools.core import move_all_assets
from stactools.cli.commands.add import create_add_command
from stactools.testing import CliTestCase
from .test_cases import TestCases


def create_temp_catalog_copy(tmp_dir):
    col = TestCases.planet_disaster()
    col.normalize_hrefs(tmp_dir)
    col.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
    move_all_assets(col, copy=True)
    col.save()

    return col


class AddTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_add_command]

    def test_add_item(self):
        catalog = TestCases.test_case_1()
        subcatalog = list(list(catalog.get_children())[0].get_children())[0]
        item = list(subcatalog.get_all_items())[0]
        item_path = item.get_self_href()
        with TemporaryDirectory() as tmp_dir:
            target_catalog = create_temp_catalog_copy(tmp_dir)

            items = list(target_catalog.get_all_items())
            self.assertEqual(len(items), 5)

            cmd = ['add', item_path, target_catalog.get_self_href()]

            self.run_command(cmd)

            target_col = pystac.read_file(target_catalog.get_self_href())
            items = list(target_col.get_all_items())
            self.assertEqual(len(items), 6)
