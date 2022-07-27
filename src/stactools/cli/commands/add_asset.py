from typing import List, Optional

import click
import pystac
import pystac.utils

from stactools.core import add_asset_to_item


def _add_asset(
    item_path: str,
    asset_key: str,
    asset_path: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    media_type: Optional[str] = None,
    roles: Optional[List[str]] = None,
    move_assets: bool = False,
    ignore_conflicts: bool = False,
) -> None:
    item = pystac.read_file(item_path)
    if not isinstance(item, pystac.Item):
        raise click.BadArgumentUsage(f"{item_path} is not a STAC Item")
    asset = pystac.Asset(asset_path, title, description, media_type, roles)
    item = add_asset_to_item(
        item,
        asset_key,
        asset,
        move_assets=move_assets,
        ignore_conflicts=ignore_conflicts,
    )
    item.save_object()


def create_add_asset_command(cli: click.Group) -> click.Command:
    @cli.command("add-asset", short_help="Add an asset to an item.")
    @click.argument("item_path")
    @click.argument("asset_key")
    @click.argument("asset_path")
    @click.option("--title", help="Optional title of the asset")
    @click.option(
        "--description",
        help=(
            "Optional description of the asset providing additional details, "
            "such as how it was processed or created."
        ),
    )
    @click.option("--media-type", help="Optional media type of the asset")
    @click.option(
        "-r",
        "--role",
        "roles",
        help="Optional, semantic roles of the asset",
        multiple=True,
    )
    @click.option(
        "--move-assets",
        is_flag=True,
        help="Move asset to the target Item's location.",
    )
    @click.option(
        "--ignore-conflicts",
        is_flag=True,
        help=(
            "If there already exists an asset with the given key or at the "
            "target path (when `--move-assets` flag is set), do not raise an "
            "error, leave the original asset from the target item in place."
        ),
    )
    def add_asset_command(
        item_path: str,
        asset_key: str,
        asset_path: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        media_type: Optional[str] = None,
        roles: Optional[List[str]] = None,
        move_assets: bool = False,
        ignore_conflicts: bool = False,
    ) -> None:
        _add_asset(
            pystac.utils.make_absolute_href(item_path),
            asset_key,
            pystac.utils.make_absolute_href(asset_path),
            title,
            description,
            media_type,
            roles,
            move_assets=move_assets,
            ignore_conflicts=ignore_conflicts,
        )

    return add_asset_command
