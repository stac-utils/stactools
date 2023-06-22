from tempfile import TemporaryDirectory

import pystac
from stactools.cli.commands.add import create_add_command
from stactools.testing import CliTestCase

from tests.utils import create_planet_disaster_clone

from .test_cases import TestCases


class AddTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_add_command]

    def test_add_item(self):
        catalog = TestCases.basic_catalog()
        subcatalog = list(list(catalog.get_children())[0].get_children())[0]
        item = list(subcatalog.get_all_items())[0]
        item_path = item.get_self_href()
        with TemporaryDirectory() as tmp_dir:
            target_catalog = create_planet_disaster_clone(tmp_dir)

            items = list(target_catalog.get_all_items())
            self.assertEqual(len(items), 5)

            cmd = ["add", item_path, target_catalog.get_self_href()]

            self.run_command(cmd)

            target_col = pystac.read_file(target_catalog.get_self_href())
            items = list(target_col.get_all_items())
            self.assertEqual(len(items), 6)

    def test_add_item_to_specific_collection(self):
        catalog = TestCases.basic_catalog()
        subcatalog = list(list(catalog.get_children())[0].get_children())[0]
        item = list(subcatalog.get_all_items())[0]
        item_path = item.get_self_href()
        with TemporaryDirectory() as tmp_dir:
            target_catalog = create_planet_disaster_clone(tmp_dir)
            items = list(target_catalog.get_all_items())
            self.assertEqual(len(items), 5)

            cmd = [
                "add",
                item_path,
                target_catalog.get_self_href(),
                "--collection",
                "hurricane-harvey",
            ]

            res = self.run_command(cmd)
            self.assertEqual(res.exit_code, 0)

            target_col = pystac.read_file(target_catalog.get_self_href())
            child_col = target_col.get_child("hurricane-harvey")
            target_item = child_col.get_item(item.id)
            self.assertIsNotNone(target_item)

    def test_add_item_to_missing_collection(self):
        catalog = TestCases.basic_catalog()
        subcatalog = list(list(catalog.get_children())[0].get_children())[0]
        item = list(subcatalog.get_all_items())[0]
        item_path = item.get_self_href()
        with TemporaryDirectory() as tmp_dir:
            target_catalog = create_planet_disaster_clone(tmp_dir)

            items = list(target_catalog.get_all_items())
            self.assertEqual(len(items), 5)

            cmd = [
                "add",
                item_path,
                target_catalog.get_self_href(),
                "--collection",
                "WRONG",
            ]

            res = self.run_command(cmd)
            self.assertEqual(res.exit_code, 2)
            self.assertTrue(" A collection with ID WRONG does not exist" in res.output)
