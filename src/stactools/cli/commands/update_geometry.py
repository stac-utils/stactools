from typing import List, Optional

import click
from click import Command, Group
from pystac import Item

from stactools.core.utils import raster_footprint


def create_update_geometry_command(cli: Group) -> Command:
    @cli.command(
        "update-geometry", short_help="Update an item geometry from an asset footprint"
    )
    @click.argument("item-path")
    @click.option(
        "-a",
        "--asset-name",
        "asset_names",
        multiple=True,
        help=(
            "The names of the assets to try for footprint extraction. "
            "The first successful footprint will be used. "
            "If no assets are provided, all assets will be tried until one is successful."
        ),
    )
    @click.option(
        "-p",
        "--precision",
        type=int,
        help="The number of decimal places to include in the coordinates for the "
        "reprojected geometry.",
        default=raster_footprint.DEFAULT_PRECISION,
    )
    @click.option(
        "-d",
        "--densification-factor",
        type=int,
        help="The factor by which to increase point density within the polygon.",
    )
    @click.option(
        "-s",
        "--simplify-tolerance",
        type=float,
        help="All points in the simplified object will be within "
        "the tolerance distance of the original geometry, in degrees.",
    )
    @click.option(
        "-n",
        "--no-data",
        type=int,
        help="explicitly set the no data value if not in image metadata",
    )
    def update_geometry_command_raster_command(
        item_path: str,
        asset_names: List[str],
        precision: int,
        densification_factor: Optional[int],
        simplify_tolerance: Optional[float],
        no_data: Optional[int],
    ) -> None:
        item = Item.from_file(item_path)
        success = raster_footprint.update_geometry_from_asset_footprint(
            item,
            asset_names=asset_names,
            precision=precision,
            densification_factor=densification_factor,
            simplify_tolerance=simplify_tolerance,
            no_data=no_data,
        )
        if success:
            item.save_object()
            click.echo(f"Item geometry updated, saved to {item.get_self_href()}")
        else:
            click.echo("Unable to update geometry")

    return update_geometry_command_raster_command
