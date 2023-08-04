import logging
import warnings
from typing import Union, cast

from pystac import Asset, Collection, Item
from pystac.utils import is_absolute_href, make_relative_href
from stactools.core.copy import move_asset_file

logger = logging.getLogger(__name__)


def add_asset(
    owner: Union[Collection, Item],
    key: str,
    asset: Asset,
    move_assets: bool = False,
    ignore_conflicts: bool = False,
) -> Union[Collection, Item]:
    """Adds an asset to an item or collection.

    Args:
        owner (Item or Collection): The PySTAC Item or Collecitonto which the asset
            will be added.
        key (str): The unique key of the asset.
        asset (Asset): The PySTAC Asset to add.
        move_assets (bool): If True, move the asset file alongside the target owner.
        ignore_conflicts (bool): If True, asset with the same key will not be added,
            and asset file that would overwrite an existing file will not be moved.
            If False, either of these situations will throw an error.

    Returns:
        owner: Returns an updated Item or Collection with the added Asset.
            This operation mutates the owner.
    """
    owner_href = owner.get_self_href()
    asset_href = asset.get_absolute_href()
    if key in owner.assets:
        if not ignore_conflicts:
            raise Exception(
                f"Target {owner} already has an asset with key {key}, "
                "cannot add asset in from {asset_href}"
            )
    else:
        if not asset_href:
            raise ValueError(
                f"Asset {asset} must have an href to be added. The href "
                "value should be an absolute path or URL."
            )
        if not owner_href and move_assets:
            raise ValueError(f"Target {owner} must have an href to move an asset to it")
        if not owner_href and not is_absolute_href(asset.href):
            raise ValueError(
                f"Target {owner} must have an href to add "
                "an asset with a relative href"
            )
        if move_assets:
            new_asset_href = move_asset_file(
                owner, asset_href, ignore_conflicts=ignore_conflicts
            )
        else:
            if not is_absolute_href(asset.href) and owner_href is not None:
                asset_href = make_relative_href(asset_href, owner_href)
            new_asset_href = asset_href
        asset.href = new_asset_href
        owner.add_asset(key, asset)
    return owner


def add_asset_to_item(
    item: Item,
    key: str,
    asset: Asset,
    move_assets: bool = False,
    ignore_conflicts: bool = False,
) -> Item:
    """Adds an asset to an item.

    Args:
        item (Item): The PySTAC Item to which the asset will be added.
        key (str): The unique key of the asset.
        asset (Asset): The PySTAC Asset to add.
        move_assets (bool): If True, move the asset file alongside the target item.
        ignore_conflicts (bool): If True, asset with the same key will not be added,
            and asset file that would overwrite an existing file will not be moved.
            If False, either of these situations will throw an error.

    Returns:
        Item: Returns an updated Item with the added Asset.
            This operation mutates the Item.
    """
    warnings.warn(
        "'add_asset_to_item' is deprecated. Use 'add_asset' instead", DeprecationWarning
    )
    return cast(
        Item,
        add_asset(
            item, key, asset, move_assets=move_assets, ignore_conflicts=ignore_conflicts
        ),
    )
