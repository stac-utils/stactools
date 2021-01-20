import os
from tempfile import TemporaryDirectory

import pystac

from stactools.corine.commands import create_corine_command
from tests.utils import (TestData, CliTestCase)


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_corine_command]

    def test_create_item(self):
        metadata_href = TestData.get_path(
            'data-files/corine/U2018_CLC2018_V2020_20u1_FR_GLP.tif.xml')

        with TemporaryDirectory() as tmp_dir:
            cmd = ['corine', 'create-item', '--cogify', metadata_href, tmp_dir]
            self.run_command(cmd)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)

        item.validate()
