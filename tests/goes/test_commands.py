import os
from tempfile import TemporaryDirectory

import pystac

from tests.utils import CliTestCase, TestData
from stactools.goes.commands import create_goes_command

EXTERNAL_DATA_PATH = (
    "goes/OR_ABI-L2-CMIPM1-M6C02_G16_s20211231619248_e20211231619306_c20211231619382.nc"
)
MULTIBAND_EXTERNAL_DATA_PATH = (
    "goes/OR_ABI-L2-MCMIPM1-M6_G16_s20211451800267_e20211451800324_c20211451800407.nc"
)


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_goes_command]

    def test_create_item(self):
        path = TestData.get_external_data(EXTERNAL_DATA_PATH)
        with TemporaryDirectory() as tmp_dir:
            args = ["goes", "create-item", path, tmp_dir]
            result = self.run_command(args)
            self.assertEqual(result.exit_code, 0)
            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)
            path = os.path.join(tmp_dir, jsons[0])
            item = pystac.read_file(path)
        item.validate()

    def test_create_item_with_cogify(self):
        path = TestData.get_external_data(EXTERNAL_DATA_PATH)
        with TemporaryDirectory() as tmp_dir:
            args = ["goes", "create-item", "--cogify", path, tmp_dir]
            result = self.run_command(args)
            self.assertEqual(result.exit_code, 0)
            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)
            path = os.path.join(tmp_dir, jsons[0])
            item = pystac.read_file(path)
            cog_data = item.assets["CMI"]
            self.assertTrue(os.path.exists(cog_data.href))
            cog_dqf = item.assets["DQF"]
            self.assertTrue(os.path.exists(cog_dqf.href))
        item.validate()

    def test_create_item_with_cogify_multiband(self):
        path = TestData.get_external_data(MULTIBAND_EXTERNAL_DATA_PATH)
        with TemporaryDirectory() as tmp_dir:
            args = ["goes", "create-item", "--cogify", path, tmp_dir]
            result = self.run_command(args)
            self.assertEqual(result.exit_code, 0)
            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)
            path = os.path.join(tmp_dir, jsons[0])
            item = pystac.read_file(path)
            for i in range(1, 17):
                cog_data = item.assets[f"CMI_C{i:02d}"]
                self.assertTrue(os.path.exists(cog_data.href))
                cog_dqf = item.assets[f"DQF_C{i:02d}"]
                self.assertTrue(os.path.exists(cog_dqf.href))
        item.validate()
