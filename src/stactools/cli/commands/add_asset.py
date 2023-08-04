from typing import List, Optional

import click
import pystac
import pystac.utils
from stactools.core import add_asset


def _add_asset(
    owner_path: str,
    asset_key: str,
    asset_path: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    media_type: Optional[str] = None,
    roles: Optional[List[str]] = None,
    move_assets: bool = False,
    ignore_conflicts: bool = False,
) -> None:
    owner = pystac.read_file(owner_path)
    if not isinstance(owner, (pystac.Item, pystac.Collection)):
        raise click.BadArgumentUsage(f"{owner_path} is not a STAC Item or Collection")
    asset = pystac.Asset(asset_path, title, description, media_type, roles)
    owner = add_asset(
        owner,
        asset_key,
        asset,
        move_assets=move_assets,
        ignore_conflicts=ignore_conflicts,
    )
    owner.save_object()


def create_add_asset_command(cli: click.Group) -> click.Command:
    @cli.command("add-asset", short_help="Add an asset to an item or collection.")
    @click.argument("owner_path")
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
        help="Move asset to the target Item or Collection's location.",
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
        owner_path: str,
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
            pystac.utils.make_absolute_href(owner_path),
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
