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
            "If no assets are provided, all assets will be tried until one is "
            "successful."
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
        "-i",
        "--densification-distance",
        type=float,
        help=(
            "The distance interval at which to increase point density within the "
            "polygon"
        ),
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
    @click.option(
        "-b",
        "--bands",
        help=(
            "Comma-separated list of bands to use to create the footprint. "
            "Use the string 'all' to choose all bands."
        ),
        default="1",
        show_default=True,
    )
    @click.option(
        "-e",
        "--skip-errors",
        help="Do not raise errors for missing hrefs or footprint calculation failures",
        type=bool,
        default=True,
        show_default=True,
    )
    def update_geometry_command_raster_command(
        item_path: str,
        asset_names: List[str],
        precision: int,
        densification_factor: Optional[int],
        densification_distance: Optional[float],
        simplify_tolerance: Optional[float],
        no_data: Optional[int],
        bands: str,
        skip_errors: bool,
    ) -> None:
        item = Item.from_file(item_path)
        if bands.lower() == "all":
            band_list = []
        else:
            band_list = list(int(band) for band in bands.split(","))
        success = raster_footprint.RasterFootprint.update_geometry_from_asset_footprint(
            item,
            asset_names=asset_names,
            precision=precision,
            densification_factor=densification_factor,
            densification_distance=densification_distance,
            simplify_tolerance=simplify_tolerance,
            no_data=no_data,
            bands=band_list,
            skip_errors=skip_errors,
        )
        if success:
            item.save_object()
            click.echo(f"Item geometry updated, saved to {item.get_self_href()}")
        else:
            click.echo("Unable to update geometry")

    return update_geometry_command_raster_command
