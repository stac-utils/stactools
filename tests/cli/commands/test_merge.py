import os
from tempfile import TemporaryDirectory

import pystac

from stactools.cli.commands.merge import create_merge_command
from stactools.core import move_all_assets
from tests.utils import (TestCases, CliTestCase)


def copy_two_planet_disaster_subsets(tmp_dir):
    """Test setup util that makes two copies of subset of the planet
    disaster data, each containing a single item. Updates the collection
    extents to match the single items.

    Returns a list of collection paths in the temporary directory.
    """
    item_ids = ['20170831_172754_101c', '20170831_162740_ssc1d1']
    new_cols = []
    for item_id in item_ids:
        col = TestCases.planet_disaster()
        for item in list(col.get_all_items()):
            if item.id != item_id:
                item.get_parent().remove_item(item.id)
        col.update_extent_from_items()
        col.normalize_hrefs(os.path.join(tmp_dir, item_id))
        col.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
        col = move_all_assets(col, copy=True)
        col.save()
        new_cols.append(col.get_self_href())

    return new_cols


class MergeTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_merge_command]

    def test_merge_moves_assets(self):
        with TemporaryDirectory() as tmp_dir:
            col_paths = copy_two_planet_disaster_subsets(tmp_dir)

            cmd = ['merge', '-a', col_paths[0], col_paths[1]]

            self.run_command(cmd)

            target_col = pystac.read_file(col_paths[1])

            items = list(target_col.get_all_items())
            self.assertEqual(len(items), 2)

            for item in items:
                for asset in item.assets.values():
                    self.assertEqual(
                        os.path.dirname(asset.get_absolute_href()),
                        os.path.dirname(item.get_self_href()))
