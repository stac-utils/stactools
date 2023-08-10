import logging
import os
import warnings
from typing import Optional, Union

import fsspec
from fsspec.core import split_protocol
from fsspec.registry import get_filesystem_class
from pystac import Catalog, CatalogType, Collection, Item
from pystac.utils import is_absolute_href, make_absolute_href, make_relative_href

logger = logging.getLogger(__name__)


def move_asset_file(
    owner: Union[Item, Collection],
    asset_href: str,
    asset_subdirectory: Optional[str] = None,
    copy: bool = False,
    ignore_conflicts: bool = False,
) -> str:
    """Moves an asset file to be alongside its owner.

    Args:
        owner (Item or Collection):
            The PySTAC Item or Collection to perform the asset transformation on.
        asset_href (str): The absolute HREF to the asset file.
        asset_subdirectory (str or None):
            A subdirectory that will be used to store the assets. If not
            supplied, the assets will be moved or copied to the same directory
            as their owner.
        copy (bool):
            If False this function will move the asset file; if True, the asset
            file will be copied.
        ignore_conflicts (bool):
            If the asset destination file already exists, this function will
            throw an error unless ignore_conflicts is True.

    Returns:
        str: The new absolute href for the asset file.
    """
    owner_href = owner.get_self_href()
    if owner_href is None:
        raise ValueError(
            f"Self HREF is not available for {owner}. This operation "
            "requires that the HREFs are available."
        )

    # TODO this shouldn't have to be absolute
    if not is_absolute_href(asset_href):
        raise ValueError("asset_href must be absolute.")

    owner_dir = os.path.dirname(owner_href)

    fname = os.path.basename(asset_href)
    if asset_subdirectory is None:
        target_dir = owner_dir
    else:
        target_dir = os.path.join(owner_dir, asset_subdirectory)
    new_asset_href = os.path.join(target_dir, fname)

    if asset_href != new_asset_href:
        dest_protocol = split_protocol(new_asset_href)[0]
        fs_dest = get_filesystem_class(dest_protocol)()
        op = None

        if fs_dest.exists(new_asset_href):
            if not ignore_conflicts:
                raise FileExistsError("{} already exists".format(new_asset_href))
        else:
            if copy:

                def _op1(dry_run: bool = False) -> None:
                    logger.info(
                        "Copying {} to {}...".format(asset_href, new_asset_href)
                    )
                    if not dry_run:
                        fs_dest.makedirs(os.path.dirname(new_asset_href), exist_ok=True)
                        with fsspec.open(asset_href, "rb") as f_src:
                            with fsspec.open(new_asset_href, "wb") as f_dst:
                                f_dst.write(f_src.read())

                op = _op1
            else:
                source_protocol = split_protocol(asset_href)[0]

                if source_protocol == dest_protocol:

                    def _op2(dry_run: bool = False) -> None:
                        logger.info(
                            "Moving {} to {}...".format(asset_href, new_asset_href)
                        )
                        if not dry_run:
                            fs_dest.makedirs(
                                os.path.dirname(new_asset_href), exist_ok=True
                            )
                            fs_dest.move(asset_href, new_asset_href)

                    op = _op2
                else:

                    def _op3(dry_run: bool = False) -> None:
                        logger.info(
                            "Moving {} to {}...".format(asset_href, new_asset_href)
                        )
                        if not dry_run:
                            fs_source = get_filesystem_class(source_protocol)()
                            fs_dest.makedirs(
                                os.path.dirname(new_asset_href), exist_ok=True
                            )
                            with fsspec.open(asset_href, "rb") as f_src:
                                with fsspec.open(new_asset_href, "wb") as f_dst:
                                    f_dst.write(f_src.read())
                            fs_source.delete(asset_href)

                    op = _op3

        if op is not None:
            op(dry_run=False)

    return new_asset_href


def move_asset_file_to_item(
    item: Item,
    asset_href: str,
    asset_subdirectory: Optional[str] = None,
    copy: bool = False,
    ignore_conflicts: bool = False,
) -> str:
    """Moves an asset file to be alongside an item.

    Args:
        item (Item):
            The PySTAC Item to perform the asset transformation on.
        asset_href (str): The absolute HREF to the asset file.
        asset_subdirectory (str or None):
            A subdirectory that will be used to store the assets. If not
            supplied, the assets will be moved or copied to the same directory
            as their item.
        copy (bool):
            If False this function will move the asset file; if True, the asset
            file will be copied.
        ignore_conflicts (bool):
            If the asset destination file already exists, this function will
            throw an error unless ignore_conflicts is True.

    Returns:
        str: The new absolute href for the asset file.
    """
    warnings.warn(
        "'move_asset_file_to_item' is deprecated. Use 'move_asset_file' instead",
        DeprecationWarning,
    )
    return move_asset_file(item, asset_href, asset_subdirectory, copy, ignore_conflicts)


def move_assets(
    owner: Optional[Union[Item, Collection]] = None,
    asset_subdirectory: Optional[str] = None,
    make_hrefs_relative: bool = True,
    copy: bool = False,
    ignore_conflicts: bool = False,
    item: Optional[Item] = None,
) -> Union[Item, Collection]:
    """Moves an Item or Collection's assets to be alongside it.

    Args:
        owner (Item or Collection):
            The PySTAC Item or Collection to perform the asset transformation on.
        asset_subdirectory (str or None):
            A subdirectory that will be used to store the assets. If not
            supplied, the assets will be moved or copied to the same directory
            as the item.
        make_assets_relative (bool):
            If True, will make the asset HREFs relative to the assets. If false,
            the asset will be an absolute href. Defaults to True.
        copy (bool):
            If False this function will move the asset file; if True,
            the asset file will be copied.
        ignore_conflicts (bool):
            If the asset destination file already exists, this function will
            throw an error unless ignore_conflicts is True.

    Returns:
        Item:
            Returns an updated item or collection.  This operation mutates
            the Item.
    """
    if item is not None:
        warnings.warn(
            "item is a deprecated option on this function. Use 'owner' instead",
            DeprecationWarning,
        )
        owner = item
    if owner is None:
        raise TypeError("move_assets missing 1 required positional argument: 'owner'")

    owner_href = owner.get_self_href()
    if owner_href is None:
        raise ValueError(
            f"Self HREF is not available for {owner}. This operation "
            "requires that HREFs are available."
        )

    for asset in owner.assets.values():
        abs_asset_href = asset.get_absolute_href()
        if abs_asset_href is None:
            raise ValueError(
                f"Asset {asset.title} HREF is not available for {owner}. "
                "This operation requires that the Asset HREFs are available."
            )
        new_asset_href = move_asset_file(
            owner,
            abs_asset_href,
            asset_subdirectory=asset_subdirectory,
            copy=copy,
            ignore_conflicts=ignore_conflicts,
        )

        if make_hrefs_relative:
            asset.href = make_relative_href(new_asset_href, owner_href)
        else:
            asset.href = new_asset_href

    return owner


def move_all_assets(
    catalog: Catalog,
    asset_subdirectory: Optional[str] = None,
    make_hrefs_relative: bool = True,
    copy: bool = False,
    ignore_conflicts: bool = False,
) -> Catalog:
    """Moves assets in a catalog to be alongside the item or collections that own them.

    Args:
        catalog (Catalog or Collection):
            The PySTAC Catalog or Collection to perform the asset transformation
            on.
        asset_subdirectory (str or None):
            A subdirectory that will be used to store the assets. If not
            supplied, the assets will be moved or copied to the same directory
            as their owner.
        make_assets_relative (bool):
            If True, will make the asset HREFs relative to the assets. If false,
            the asset will be an absolute href.
        copy (bool):
            If False this function will move the asset file; if True, the asset
            file will be copied.
        ignore_conflicts (bool):
            If the asset destination file already exists, this function will
            throw an error unless ignore_conflicts is True.

    Returns:
        Catalog or Collection:
            Returns the updated catalog or collection.  This operation mutates
            the catalog or collection.
    """

    for item in catalog.get_items(recursive=True):
        move_assets(
            item, asset_subdirectory, make_hrefs_relative, copy, ignore_conflicts
        )

    for collection in catalog.get_all_collections():
        move_assets(
            collection, asset_subdirectory, make_hrefs_relative, copy, ignore_conflicts
        )

    return catalog


def copy_catalog(
    source_catalog: Catalog,
    dest_directory: str,
    catalog_type: Optional[CatalogType] = None,
    copy_assets: bool = False,
    publish_location: Optional[str] = None,
    resolve_links: bool = True,
) -> None:
    if resolve_links:
        catalog = source_catalog.full_copy()
    else:
        catalog = source_catalog.clone()
        catalog.set_root(catalog)

    dest_directory = make_absolute_href(dest_directory)
    if copy_assets:
        catalog.make_all_asset_hrefs_absolute()
        catalog.normalize_hrefs(dest_directory, skip_unresolved=not resolve_links)
        catalog = move_all_assets(catalog, copy=True, make_hrefs_relative=True)

    if publish_location is not None:
        catalog.normalize_hrefs(publish_location, skip_unresolved=not resolve_links)
        catalog.save(catalog_type, dest_directory)
    else:
        catalog.normalize_hrefs(dest_directory, skip_unresolved=not resolve_links)
        catalog.save(catalog_type)
