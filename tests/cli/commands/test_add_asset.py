import os
from tempfile import TemporaryDirectory
from typing import Callable, List

import pystac
import pystac.utils
from click import Command, Group
from pystac import Item

from stactools.cli.commands.add_asset import create_add_asset_command
from stactools.testing.cli_test import CliTestCase
from tests import test_data
from tests.utils import create_temp_copy


class AddAssetTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_add_asset_command]

    def test_add_asset_to_item(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            item_path = create_temp_copy(
                test_data.get_path("data-files/core/simple-item.json"),
                tmp_dir,
                "item.json",
            )
            item = Item.from_file(item_path)
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

            item = Item.from_file(item_path)
            asset = item.assets["test-asset"]
            assert isinstance(asset, pystac.Asset), asset
            assert asset.href is not None, asset.to_dict()
            assert os.path.isfile(asset.href), asset.to_dict()
            assert asset.title == "test", asset.to_dict()
            assert asset.description == "placeholder asset", asset.to_dict()
            assert asset.roles
            self.assertListEqual(asset.roles, ["thumbnail", "overview"])

    def test_add_asset_to_item_with_relative_paths(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            item_path = create_temp_copy(
                test_data.get_path("data-files/core/simple-item.json"),
                tmp_dir,
                "item.json",
            )
            asset_path = test_data.get_path("data-files/core/byte.tif")
            cmd = [
                "add-asset",
                pystac.utils.make_relative_href(
                    item_path, os.getcwd(), start_is_dir=True
                ),
                "test-asset",
                pystac.utils.make_relative_href(
                    asset_path, os.getcwd(), start_is_dir=True
                ),
            ]
            result = self.run_command(cmd)
            self.assertEqual(result.exit_code, 0)
