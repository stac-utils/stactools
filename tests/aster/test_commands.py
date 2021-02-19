import os
from tempfile import TemporaryDirectory

import pystac

from stactools.aster.constants import HDF_ASSET_KEY
from stactools.aster.commands import create_aster_command
from tests.utils import (TestData, CliTestCase)

EXTERNAL_DATA_PATH = 'aster/AST_L1T_00301012006003619_20150512141939_7778.hdf'


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_aster_command]

    def test_create_item(self):
        test_path = TestData.get_external_data(EXTERNAL_DATA_PATH)

        with TemporaryDirectory() as tmp_dir:
            cmd = ['aster', 'create-item', '--cogify', test_path, tmp_dir]
            self.run_command(cmd)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)

        item.validate()
        self.assertEqual(set(item.assets.keys()),
                         set([HDF_ASSET_KEY, 'VNIR', 'SWIR', 'TIR']))
