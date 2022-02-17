import os

from pystac import Catalog, Item, Collection
from pystac.layout import BestPracticesLayoutStrategy

from stactools.core.copy import move_assets as do_move_assets


def add_item(source_item: Item,
             target_catalog: Catalog,
             move_assets: bool = False) -> None:
    """Add a item into a catalog.

    Args:
        source_item (pystac.Item): The Item that will be added.
            This item is not mutated in this operation.
        target_catalog (pystac.Item): The destination catalog.
            This catalog will be mutated in this operation.
        move_assets (bool): If true, move the asset files alongside the target item.
    """

    target_item_ids = [item.id for item in target_catalog.get_all_items()]
    if source_item.id in target_item_ids:
        raise ValueError(
            f'An item with ID {source_item.id} already exists in the target catalog'
        )
    self_href = target_catalog.get_self_href()
    if self_href:
        parent_dir = os.path.dirname(self_href)
        layout_strategy = BestPracticesLayoutStrategy()
        item_copy = source_item.clone()
        item_copy.set_self_href(
            layout_strategy.get_item_href(item_copy, parent_dir))
        target_catalog.add_item(item_copy)

        if isinstance(target_catalog, Collection):
            item_copy.set_collection(target_catalog)
            target_catalog.update_extent_from_items()
        else:
            item_copy.set_collection(None)

        if move_assets:
            do_move_assets(item_copy, copy=False)
    else:
        raise ValueError(
            f"Cannot add Item {source_item.id} because {target_catalog} does not have a self href."
        )
