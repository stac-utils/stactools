import os
import shutil
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
        move_all_assets(col, copy=True)
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

    def test_merge_as_child(self):
        with TemporaryDirectory() as tmp_dir:
            col_paths = copy_two_planet_disaster_subsets(tmp_dir)

            cmd = ['merge', '-a', "-c", col_paths[0], col_paths[1]]

            self.run_command(cmd)

            target_col = pystac.read_file(col_paths[1])

            links = list(target_col.get_child_links())
            self.assertEqual(2, len(links))
            for child in links:
                self.assertTrue(os.path.exists(child.get_absolute_href()))

    def test_merge_updates_collection_extent(self):
        with TemporaryDirectory() as tmp_dir:
            col_paths = copy_two_planet_disaster_subsets(tmp_dir)

            extent1 = pystac.read_file(col_paths[0]).extent
            extent2 = pystac.read_file(col_paths[1]).extent

            xmin = min(
                [extent1.spatial.bboxes[0][0], extent2.spatial.bboxes[0][0]])
            time_max = max([
                extent1.temporal.intervals[0][1],
                extent2.temporal.intervals[0][1],
            ])

            cmd = ['merge', col_paths[0], col_paths[1]]

            self.run_command(cmd)

            result_extent = pystac.read_file(col_paths[1]).extent

            def set_of_values(x):
                result = set([])
                if type(x) is dict:
                    result |= set_of_values(list(x.values()))
                elif type(x) is list:
                    for e in x:
                        if type(e) is list:
                            result |= set_of_values(e)
                        else:
                            result.add(e)
                return result

            # Make sure it didn't just carry forward the old extent
            self.assertNotEqual(set_of_values(result_extent.spatial.bboxes),
                                set_of_values(extent2.spatial.bboxes))

            self.assertNotEqual(
                set_of_values(result_extent.temporal.intervals),
                set_of_values(extent2.temporal.intervals))

            self.assertEqual(result_extent.spatial.bboxes[0][0], xmin)
            self.assertEqual(result_extent.temporal.intervals[0][1], time_max)

    def test_merges_assets(self):
        item_id = '2017831_195552_SS02'

        with TemporaryDirectory() as tmp_dir:
            orig_data = os.path.dirname(
                TestCases.planet_disaster().get_self_href())
            shutil.copytree(orig_data, os.path.join(tmp_dir, '0'))

            col0 = pystac.read_file(os.path.join(tmp_dir, '0/collection.json'))
            item = col0.get_item(item_id, recursive=True)

            new_col1 = col0.clone()
            new_col1.clear_children()

            item1 = item.clone()
            del item1.assets['visual']
            new_col1.add_item(item1)

            new_col1.normalize_hrefs(os.path.join(tmp_dir, 'a'))
            new_col1.save()

            new_col2 = col0.clone()
            new_col2.clear_children()

            item2 = item.clone()
            del item2.assets['full-jpg']
            new_col2.add_item(item2)

            new_col2.normalize_hrefs(os.path.join(tmp_dir, 'b'))
            new_col2.save()

            cmd = [
                'merge',
                os.path.join(tmp_dir, 'a/collection.json'),
                os.path.join(tmp_dir, 'b/collection.json'), '--move-assets',
                '--ignore-conflicts'
            ]

            self.run_command(cmd)

            target_col = pystac.read_file(
                os.path.join(tmp_dir, 'b/collection.json'))

            result_item = target_col.get_item(item_id, recursive=True)
            self.assertIn('visual', result_item.assets)
            self.assertIn('full-jpg', result_item.assets)
