import os
from tempfile import TemporaryDirectory

import pystac

from stactools.modis.commands import create_modis_command
from tests.utils import (TestData, CliTestCase)


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_modis_command]

    def test_create_item(self):
        metadata_href = TestData.get_path(
            'data-files/modis/MCD12Q1.A2001001.h00v08.006.2018142182903.hdf.xml'
        )

        with TemporaryDirectory() as tmp_dir:
            cmd = ['modis', 'create-item', '--cogify', metadata_href, tmp_dir]
            self.run_command(cmd)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]

            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)

        item.validate()
