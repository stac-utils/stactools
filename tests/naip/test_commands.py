import os
from tempfile import TemporaryDirectory

import pystac

from stactools.naip.commands import create_naip_command
from tests.utils import (TestData, CliTestCase)


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_naip_command]

    def test_create_item(self):
        fgdc_href = TestData.get_path(
            'data-files/naip/m_3008501_ne_16_1_20110815.txt')
        cog_href = TestData.get_path(
            'data-files/naip/m_3008501_ne_16_1_20110815-downsampled.tif')

        with TemporaryDirectory() as tmp_dir:
            cmd = ['naip', 'create-item', 'al', fgdc_href, cog_href, tmp_dir]
            self.run_command(cmd)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)

        item.validate()

    def test_create_item_no_resource_desc(self):
        fgdc_href = TestData.get_path(
            'data-files/naip/m_4207201_ne_18_h_20160809.txt')
        cog_href = (
            'https://naipeuwest.blob.core.windows.net/'
            'naip/v002/vt/2016/vt_060cm_2016/42072/m_4207201_ne_18_h_20160809.tif'
        )

        with TemporaryDirectory() as tmp_dir:
            cmd = ['naip', 'create-item', 'al', fgdc_href, cog_href, tmp_dir]
            self.run_command(cmd)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)

        item.validate()
