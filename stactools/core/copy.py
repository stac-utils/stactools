import os
import logging

import fsspec
from fsspec.core import split_protocol
from fsspec.registry import get_filesystem_class

from pystac.utils import (is_absolute_href, make_absolute_href,
                          make_relative_href)

logger = logging.getLogger(__name__)


def move_asset_file_to_item(item,
                            asset_href,
                            asset_subdirectory=None,
                            copy=False,
                            ignore_conflicts=False):
    """Moves an asset file to be alongside that item.

    Args:
        item (Item): The PySTAC Item
            to perform the asset transformation on.
        asset_href (str): The absolute HREF to the asset file.
        asset_subdirectory (str or None): A subdirectory that will be used
            to store the assets. If not supplied, the assets will be moved
            or copied to the same directory as their item.
        copy (bool): If False this function will move the asset file; if True,
            the asset file will be copied.
        ignore_conflicts (bool): If the asset destination file already exists,
            this function will throw an error unless ignore_conflicts is True.

    Returns:
        str: The new absolute href for the asset file
    """
    item_href = item.get_self_href()
    if item_href is None:
        raise ValueError(
            'Self HREF is not available for item {}. This operation '
            'requires that the Item HREFs are available.')

    if not is_absolute_href(asset_href):
        raise ValueError('asset_href msut be absolute.')

    item_dir = os.path.dirname(item_href)

    fname = os.path.basename(asset_href)
    if asset_subdirectory is None:
        target_dir = item_dir
    else:
        target_dir = os.path.join(item_dir, asset_subdirectory)
    new_asset_href = os.path.join(target_dir, fname)

    if asset_href != new_asset_href:
        dest_protocol = split_protocol(new_asset_href)[0]
        fs_dest = get_filesystem_class(dest_protocol)()
        op = None

        if fs_dest.exists(new_asset_href):
            if not ignore_conflicts:
                raise FileExistsError(
                    '{} already exists'.format(new_asset_href))
        else:
            if copy:

                def _op1(dry_run=False):
                    logger.info("Copying {} to {}...".format(
                        asset_href, new_asset_href))
                    if not dry_run:
                        fs_dest.makedirs(os.path.dirname(new_asset_href),
                                         exist_ok=True)
                        with fsspec.open(asset_href, 'rb') as f_src:
                            with fsspec.open(new_asset_href, 'wb') as f_dst:
                                f_dst.write(f_src.read())

                op = _op1
            else:
                source_protocol = split_protocol(asset_href)[0]

                if source_protocol == dest_protocol:

                    def _op2(dry_run=False):
                        logger.info("Moving {} to {}...".format(
                            asset_href, new_asset_href))
                        if not dry_run:
                            fs_dest.makedirs(os.path.dirname(new_asset_href),
                                             exist_ok=True)
                            fs_dest.move(asset_href, new_asset_href)

                    op = _op2
                else:

                    def _op3(dry_run=False):
                        logger.info("Moving {} to {}...".format(
                            asset_href, new_asset_href))
                        if not dry_run:
                            fs_source = get_filesystem_class(source_protocol)()
                            fs_dest.makedirs(os.path.dirname(new_asset_href),
                                             exist_ok=True)
                            with fsspec.open(asset_href, 'rb') as f_src:
                                with fsspec.open(new_asset_href,
                                                 'wb') as f_dst:
                                    f_dst.write(f_src.read())
                            fs_source.delete(asset_href)

                    op = _op3

        if op is not None:
            op(dry_run=False)

    return new_asset_href


def move_assets(item,
                asset_subdirectory=None,
                make_hrefs_relative=True,
                copy=False,
                ignore_conflicts=False):
    """Moves assets for an item to be alongside that item.

    Args:
        item (Item): The PySTAC Item
            to perform the asset transformation on.
        asset_subdirectory (str or None): A subdirectory that will be used
            to store the assets. If not supplied, the assets will be moved
            or copied to the same directory as their item.
        make_assets_relative (bool): If True, will make the asset HREFs relative
            to the assets. If false, the asset will be an absolute href.
        copy (bool): If False this function will move the asset file; if True,
            the asset file will be copied.
        ignore_conflicts (bool): If the asset destination file already exists,
            this function will throw an error unless ignore_conflicts is True.

    Returns:
        Item: Returns an updated catalog or collection.
            This operation mutates the Item.
    """
    item_href = item.get_self_href()
    if item_href is None:
        raise ValueError(
            'Self HREF is not available for item {}. This operation '
            'requires that the Item HREFs are available.')

    for asset in item.assets.values():
        abs_asset_href = asset.get_absolute_href()

        new_asset_href = move_asset_file_to_item(
            item,
            abs_asset_href,
            asset_subdirectory=asset_subdirectory,
            copy=copy,
            ignore_conflicts=ignore_conflicts)

        if make_hrefs_relative:
            asset.href = make_relative_href(new_asset_href, item_href)
        else:
            asset.href = new_asset_href

    return item


def move_all_assets(catalog,
                    asset_subdirectory=None,
                    make_hrefs_relative=True,
                    copy=False,
                    ignore_conflicts=False):
    """Moves assets in a catalog to be alongside the items that own them.

    Args:
        catalog (Catalog or Collection): The PySTAC Catalog or Collection
            to perform the asset transformation on.
        asset_subdirectory (str or None): A subdirectory that will be used
            to store the assets. If not supplied, the assets will be moved
            or copied to the same directory as their item.
        make_assets_relative (bool): If True, will make the asset HREFs relative
            to the assets. If false, the asset will be an absolute href.
        copy (bool): If False this function will move the asset file; if True,
            the asset file will be copied.
        ignore_conflicts (bool): If the asset destination file already exists,
            this function will throw an error unless ignore_conflicts is True.

    Returns:
        [Catalog or Collection]: Returns the updated catalog.
            This operation mutates the catalog.
    """

    for item in catalog.get_all_items():
        move_assets(item, asset_subdirectory, make_hrefs_relative, copy,
                    ignore_conflicts)

    return catalog


def copy_catalog(source_catalog,
                 dest_directory,
                 catalog_type=None,
                 copy_assets=False):
    catalog = source_catalog.full_copy()
    dest_directory = make_absolute_href(dest_directory)

    catalog.normalize_hrefs(dest_directory)

    if copy_assets:
        catalog = move_all_assets(catalog, copy=True, make_hrefs_relative=True)

    catalog.save(catalog_type)
