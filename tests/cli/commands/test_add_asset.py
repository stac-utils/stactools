import os

import pystac
import pystac.utils
from click.testing import CliRunner

from stactools.cli.cli import cli
from tests import test_data


def test_add_asset_to_item(tmp_item_path: str) -> None:
    asset_path = test_data.get_path("data-files/core/byte.tif")
    item_path = tmp_item_path
    item = pystac.Item.from_file(item_path)
    assert "test-asset" not in item.assets

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
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
        ],
    )
    assert result.exit_code == 0

    item = pystac.Item.from_file(item_path)
    asset = item.assets["test-asset"]
    assert isinstance(asset, pystac.Asset), asset
    assert asset.href is not None, asset.to_dict()
    assert os.path.isfile(asset.href), asset.to_dict()
    assert asset.title == "test", asset.to_dict()
    assert asset.description == "placeholder asset", asset.to_dict()
    assert asset.roles == ["thumbnail", "overview"]


def test_add_asset_to_item_with_relative_paths(tmp_item_path: str) -> None:
    asset_path = test_data.get_path("data-files/core/byte.tif")
    item_path = tmp_item_path
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "add-asset",
            pystac.utils.make_relative_href(item_path, os.getcwd(), start_is_dir=True),
            "test-asset",
            pystac.utils.make_relative_href(asset_path, os.getcwd(), start_is_dir=True),
        ],
    )
    assert result.exit_code == 0
