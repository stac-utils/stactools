import os
from tempfile import TemporaryDirectory
from unittest import TestCase

import pystac

from stactools.core import add_asset_to_item
from tests import test_data
from tests.utils import create_temp_copy


class AddAssetTest(TestCase):
    def test_add_asset_to_item(self):
        """Test adding an asset to an item without moving the asset"""
        item_path = test_data.get_path("data-files/core/simple-item.json")
        item = pystac.read_file(item_path)
        assert isinstance(item, pystac.Item)
        assert "test-asset" not in item.assets

        asset_path = test_data.get_path("data-files/core/byte.tif")
        asset = pystac.Asset(
            asset_path, "test", "placeholder asset", roles=["thumbnail", "overview"]
        )
        item = add_asset_to_item(item, "test-asset", asset)

        asset = item.assets["test-asset"]
        assert isinstance(asset, pystac.Asset), asset
        assert asset.href is not None, asset.to_dict()
        assert os.path.isfile(asset.href), asset.to_dict()
        assert asset.title == "test", asset.to_dict()
        assert asset.description == "placeholder asset", asset.to_dict()
        self.assertListEqual(asset.roles, ["thumbnail", "overview"])

    def test_add_asset_move(self):
        """Test adding an asset to an item and moving it to the item"""
        with TemporaryDirectory() as tmp_dir:
            item_path = create_temp_copy(
                test_data.get_path("data-files/core/simple-item.json"),
                tmp_dir,
                "item.json",
            )
            item = pystac.read_file(item_path)
            with TemporaryDirectory() as tmp_dir2:
                asset_path = create_temp_copy(
                    test_data.get_path("data-files/core/byte.tif"), tmp_dir2, "test.tif"
                )
                asset = pystac.Asset(
                    asset_path,
                    "test",
                    "placeholder asset",
                    roles=["thumbnail", "overview"],
                )
                item = add_asset_to_item(
                    item, "test-asset", asset, move_assets=True, ignore_conflicts=True
                )

                asset = item.assets["test-asset"]
                assert isinstance(asset, pystac.Asset), asset
                assert asset.href is not None, asset.to_dict()
                assert os.path.isfile(asset.href), asset.to_dict()
                self.assertEqual(
                    os.path.dirname(asset.get_absolute_href()),
                    os.path.dirname(item.get_self_href()),
                )

    def test_add_and_move_with_missing_item_href(self):
        """Test that adding an asset with `move_assets` set to True raises an
        error if the item doesn't have an href
        """
        item_path = test_data.get_path("data-files/core/simple-item.json")
        item = pystac.read_file(item_path)
        item.set_self_href(None)

        asset_path = test_data.get_path("data-files/core/byte.tif")
        asset = pystac.Asset(
            asset_path, "test", "placeholder asset", roles=["thumbnail", "overview"]
        )
        with self.assertRaises(ValueError):
            add_asset_to_item(item, "test-asset", asset, move_assets=True)

    def test_add_with_missing_item_href_relative_asset_href(self):
        """Test that adding an asset with a relative href raises an error if
        the item doesn't have an href
        """
        item_path = test_data.get_path("data-files/core/simple-item.json")
        item = pystac.read_file(item_path)
        item.set_self_href(None)

        asset = pystac.Asset(
            "data-files/core/byte.tif",
            "test",
            "placeholder asset",
            roles=["thumbnail", "overview"],
        )
        with self.assertRaises(ValueError):
            add_asset_to_item(item, "test-asset", asset)

    def test_add_with_missing_item_href_absolute_asset_href(self):
        """Test that adding an asset with an absolute href works even if the
        item doesn't have an href
        """
        item_path = test_data.get_path("data-files/core/simple-item.json")
        item = pystac.read_file(item_path)
        item.set_self_href(None)

        asset_path = test_data.get_path("data-files/core/byte.tif")
        asset = pystac.Asset(
            asset_path, "test", "placeholder asset", roles=["thumbnail", "overview"]
        )
        add_asset_to_item(item, "test-asset", asset)
        asset = item.assets["test-asset"]
        assert isinstance(asset, pystac.Asset), asset

    def test_missing_asset_href(self):
        """Test that adding an asset with a missing href raises an error"""
        item_path = test_data.get_path("data-files/core/simple-item.json")
        item = pystac.read_file(item_path)

        asset = pystac.Asset(
            "", "test", "placeholder asset", roles=["thumbnail", "overview"]
        )
        with self.assertRaises(ValueError):
            add_asset_to_item(item, "test-asset", asset)

    def test_add_asset_ignore_conflict(self):
        """Test that adding an asset with an existing key doesn't raise any
        errors if `ignore_conflict` is set to True"""
        item_path = test_data.get_path("data-files/core/simple-item.json")
        item = pystac.read_file(item_path)

        asset_path = test_data.get_path("data-files/core/byte.tif")
        asset = pystac.Asset(
            asset_path, "test", "placeholder asset", roles=["thumbnail", "overview"]
        )

        with self.assertRaises(Exception):
            add_asset_to_item(item, "thumbnail", asset)
        item = add_asset_to_item(item, "thumbnail", asset, ignore_conflicts=True)
        assert item.assets["thumbnail"].title == "Thumbnail"
