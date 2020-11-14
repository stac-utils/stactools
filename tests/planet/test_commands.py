import os
import unittest
from tempfile import TemporaryDirectory

import click
from click.testing import CliRunner
import pystac

from stactools.planet.commands import create_planet_command
from tests.utils import TestCases


class ConvertOrderTest(unittest.TestCase):
    def setUp(self):
        @click.group()
        def cli():
            pass

        create_planet_command(cli)
        self.cli = cli

    def test_converts(self):
        test_order_manifest = TestCases.get_path(
            'data-files/planet-order/manifest.json')

        with TemporaryDirectory() as tmp_dir:
            runner = CliRunner()
            result = runner.invoke(self.cli, [
                'planet', 'convert-order', test_order_manifest, tmp_dir,
                'test_id', 'A test catalog', '--title', 'test-catalog', '-a',
                'copy'
            ],
                                   catch_exceptions=False)

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

            self.assertEqual(item.properties.get('pl:quality_category'), 'standard')
