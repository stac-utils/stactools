import os
from tempfile import TemporaryDirectory

import pystac
from pystac.utils import is_absolute_href, make_absolute_href

from stactools.cli.commands.copy import create_copy_command, create_move_assets_command
from tests.utils import (TestCases, CliTestCase)


class CopyTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_copy_command, create_move_assets_command]

    def test_copy(self):
        cat = TestCases.planet_disaster()
        item_ids = set([i.id for i in cat.get_all_items()])
        with TemporaryDirectory() as tmp_dir:
            self.run_command(['copy', cat.get_self_href(), tmp_dir])

            copy_cat = pystac.read_file(
                os.path.join(tmp_dir, 'collection.json'))
            copy_cat_ids = set([i.id for i in copy_cat.get_all_items()])

            self.assertEqual(copy_cat_ids, item_ids)

    def test_copy_to_relative(self):
        cat = TestCases.planet_disaster()

        with TemporaryDirectory() as tmp_dir:
            cat.make_all_asset_hrefs_absolute()
            cat.normalize_hrefs(tmp_dir)
            cat.save(catalog_type=pystac.CatalogType.ABSOLUTE_PUBLISHED)

            cat2_dir = os.path.join(tmp_dir, 'second')

            command = [
                'copy', '-t', 'SELF_CONTAINED', '-a',
                cat.get_self_href(), cat2_dir
            ]
            self.run_command(command)
            cat2 = pystac.read_file(os.path.join(cat2_dir, 'collection.json'))
            for item in cat2.get_all_items():
                item_href = item.get_self_href()
                for asset in item.assets.values():
                    href = asset.href
                    self.assertFalse(is_absolute_href(href))
                    common_path = os.path.commonpath([
                        os.path.dirname(item_href),
                        make_absolute_href(href, item_href)
                    ])
                    self.assertTrue(common_path, os.path.dirname(item_href))

    def test_move_assets(self):
        cat = TestCases.planet_disaster()

        with TemporaryDirectory() as tmp_dir:
            cat.normalize_hrefs(tmp_dir)
            cat.save(catalog_type=pystac.CatalogType.RELATIVE_PUBLISHED)
            cat_href = cat.get_self_href()

            command = ['move-assets', '-c', cat_href]
            self.assertEqual(self.run_command(command).exit_code, 0)
            cat2 = pystac.read_file(cat_href)
            for item in cat2.get_all_items():
                item_href = item.get_self_href()
                for asset in item.assets.values():
                    href = asset.href

                    self.assertFalse(is_absolute_href(href))
                    common_path = os.path.commonpath([
                        os.path.dirname(item_href),
                        make_absolute_href(href, item_href)
                    ])

                    self.assertEqual(common_path, os.path.dirname(item_href))
