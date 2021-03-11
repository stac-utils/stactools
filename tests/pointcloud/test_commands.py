import os
from tempfile import TemporaryDirectory

import pystac

from stactools.pointcloud.commands import create_pointcloud_command
from tests.utils import (TestData, CliTestCase)


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_pointcloud_command]

    def test_create_item(self):
        href = TestData.get_path('data-files/pointcloud/autzen_trim.las')
        with TemporaryDirectory() as directory:
            cmd = ['pointcloud', 'create-item', href, directory]
            self.run_command(cmd)
            jsons = [p for p in os.listdir(directory) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)
            item_path = os.path.join(directory, jsons[0])
            item = pystac.read_file(item_path)
        item.validate()
