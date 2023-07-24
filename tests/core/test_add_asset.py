import os
import shutil
from pathlib import Path

import pystac
import pytest
from stactools.core import add_asset, add_asset_to_item

from tests import test_data


@pytest.fixture(scope="function")
def item() -> pystac.Item:
    return pystac.Item.from_file(test_data.get_path("data-files/core/simple-item.json"))


def test_add_asset_to_item(item: pystac.Item) -> None:
    """Test adding an asset to an item without moving the asset"""
    assert "test-asset" not in item.assets
    asset = pystac.Asset(
        test_data.get_path("data-files/core/byte.tif"),
        "test",
        "placeholder asset",
        roles=["thumbnail", "overview"],
    )
    with pytest.warns(DeprecationWarning, match="Use 'add_asset' instead"):
        item = add_asset_to_item(item, "test-asset", asset)

    asset = item.assets["test-asset"]
    assert isinstance(asset, pystac.Asset), asset
    assert asset.href is not None, asset.to_dict()
    assert os.path.isfile(asset.href), asset.to_dict()
    assert asset.title == "test", asset.to_dict()
    assert asset.description == "placeholder asset", asset.to_dict()
    assert asset.roles == ["thumbnail", "overview"]


@pytest.mark.parametrize(
    "path",
    [
        "data-files/core/simple-item.json",
        "data-files/catalogs/collection-assets/sentinel-2/collection.json",
    ],
)
def test_add_asset_move(path: str, tmp_path: Path, tmp_asset_path: str) -> None:
    """Test adding and moving an asset to an item or collection"""
    src = test_data.get_path(path)
    dst = obj_path = tmp_path / "obj.json"
    shutil.copyfile(src, str(dst))

    asset = pystac.Asset(
        tmp_asset_path,
        "test",
        "placeholder asset",
        roles=["thumbnail", "overview"],
    )
    obj = pystac.read_file(obj_path)

    obj = add_asset(obj, "test-asset", asset, move_assets=True, ignore_conflicts=True)

    asset = obj.assets["test-asset"]
    assert isinstance(asset, pystac.Asset), asset
    assert asset.href is not None, asset.to_dict()
    assert os.path.isfile(asset.href), asset.to_dict()
    asset_absolute_href = asset.get_absolute_href()
    assert asset_absolute_href
    obj_self_href = obj.get_self_href()
    assert obj_self_href
    assert os.path.dirname(asset_absolute_href) == os.path.dirname(obj_self_href)


def test_add_and_move_with_missing_item_href(item: pystac.Item) -> None:
    """Test that adding an asset with `move_assets` set to True raises an
    error if the item doesn't have an href
    """
    item.set_self_href(None)
    asset = pystac.Asset(
        test_data.get_path("data-files/core/byte.tif"),
        "test",
        "placeholder asset",
        roles=["thumbnail", "overview"],
    )
    with pytest.raises(ValueError):
        add_asset(item, "test-asset", asset, move_assets=True)


def test_add_with_missing_item_href_relative_asset_href(item: pystac.Item) -> None:
    """Test that adding an asset with a relative href raises an error if
    the item doesn't have an href
    """
    item.set_self_href(None)
    asset = pystac.Asset(
        "data-files/core/byte.tif",
        "test",
        "placeholder asset",
        roles=["thumbnail", "overview"],
    )
    with pytest.raises(ValueError):
        add_asset(item, "test-asset", asset)


def test_add_with_missing_item_href_absolute_asset_href(item: pystac.Item) -> None:
    """Test that adding an asset with an absolute href works even if the
    item doesn't have an href
    """
    item.set_self_href(None)
    asset = pystac.Asset(
        test_data.get_path("data-files/core/byte.tif"),
        "test",
        "placeholder asset",
        roles=["thumbnail", "overview"],
    )
    add_asset(item, "test-asset", asset)
    asset = item.assets["test-asset"]
    assert isinstance(asset, pystac.Asset), asset


def test_missing_asset_href(item: pystac.Item) -> None:
    """Test that adding an asset with a missing href raises an error"""
    asset = pystac.Asset(
        "", "test", "placeholder asset", roles=["thumbnail", "overview"]
    )
    with pytest.raises(ValueError):
        add_asset(item, "test-asset", asset)


def test_add_asset_ignore_conflict(item: pystac.Item) -> None:
    """Test that adding an asset with an existing key doesn't raise any
    errors if `ignore_conflict` is set to True"""
    asset = pystac.Asset(
        test_data.get_path("data-files/core/byte.tif"),
        "test",
        "placeholder asset",
        roles=["thumbnail", "overview"],
    )

    with pytest.raises(Exception):
        add_asset(item, "thumbnail", asset)
    item = add_asset(item, "thumbnail", asset, ignore_conflicts=True)
    assert item.assets["thumbnail"].title == "Thumbnail"
