import os
from tempfile import TemporaryDirectory

import pystac

from stactools.cli.commands.add_asset import create_add_asset_command
from stactools.testing import CliTestCase
from tests import test_data
from tests.utils import create_temp_copy


class AddAssetTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_add_asset_command]

    def test_add_asset_to_item(self):
        with TemporaryDirectory() as tmp_dir:
            item_path = create_temp_copy(
                test_data.get_path("data-files/core/simple-item.json"),
                tmp_dir,
                "item.json",
            )
            item = pystac.read_file(item_path)
            assert "test-asset" not in item.assets

            asset_path = test_data.get_path("data-files/core/byte.tif")
            cmd = [
                "add-asset",
                item_path,
                "test-asset",
                asset_path,
                "--title",
                "test",
                "--description",
                "placeholder asset",
                "--role",
                "thumbnail",
                "--role",
                "overview",
            ]
            res = self.run_command(cmd)
            self.assertEqual(res.exit_code, 0)

            item = pystac.read_file(item_path)
            asset = item.assets["test-asset"]
            assert isinstance(asset, pystac.Asset), asset
            assert asset.href is not None, asset.to_dict()
            assert os.path.isfile(asset.href), asset.to_dict()
            assert asset.title == "test", asset.to_dict()
            assert asset.description == "placeholder asset", asset.to_dict()
            self.assertListEqual(asset.roles, ["thumbnail", "overview"])
