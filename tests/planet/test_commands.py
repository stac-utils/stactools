import os
from tempfile import TemporaryDirectory

import pystac

from stactools.planet.commands import create_planet_command
from tests.utils import (TestData, CliTestCase)


class ConvertOrderTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_planet_command]

    def tearDown(self):
        thumbnail_path = TestData.get_path(
            "data-files/planet-order/files/"
            "20180119_XXXXXXX_XXXX_3B_Visual_file_format.thumbnail.png")
        thumbnail_metadata_path = "{}.aux.xml".format(thumbnail_path)
        for path in [thumbnail_path, thumbnail_metadata_path]:
            if os.path.exists(path):
                os.remove(path)

    def test_converts(self):
        test_order_manifest = TestData.get_path(
            'data-files/planet-order/manifest.json')

        with TemporaryDirectory() as tmp_dir:
            result = self.run_command([
                'planet', 'convert-order', test_order_manifest, tmp_dir,
                'test_id', 'A test catalog', '--title', 'test-catalog', '-a',
                'copy'
            ])

            self.assertEqual(result.exit_code,
                             0,
                             msg='\n{}'.format(result.output))

            collection = pystac.read_file(
                os.path.join(tmp_dir, 'collection.json'))
            item_ids = set([i.id for i in collection.get_all_items()])

            self.assertEqual(item_ids, set(['20180119_XXXXXXX_XXXX']))
            item = collection.get_item('20180119_XXXXXXX_XXXX')
            for asset in item.assets.values():
                self.assertTrue(os.path.exists(asset.get_absolute_href()))
                self.assertEqual(os.path.dirname(asset.get_absolute_href()),
                                 os.path.dirname(item.get_self_href()))

            self.assertEqual(item.properties.get('pl:quality_category'),
                             'standard')
