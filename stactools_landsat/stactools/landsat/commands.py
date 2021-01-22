import json
import os
import sys

import click
from pystac import Item
from stactools.landsat.utils import (transform_mtl_to_stac,
                                     transform_stac_to_stac)


def create_landsat_command(cli):
    """Creates a command group for working
    with Landsat metadata from USGS' Collection 2
    """
    @cli.group(
        'landsat',
        short_help=("Commands for working with Landsat Collection 2 metadata.")
    )
    def landsat():
        pass

    @landsat.command("convert",
                     short_help="Convert a Landsat MTL file to a STAC Item")
    @click.option("--mtl", "-m", help="Path to an MTL file.")
    @click.option("--stac", "-s", help="Path to a STAC file.")
    @click.option(
        "--enable-proj",
        "-p",
        default=True,
        is_flag=True,
        help="Enable the proj extension. Requires access to blue band.")
    @click.option("--dst", "-d", help="Output directory")
    def landsat_command(mtl, stac, enable_proj, dst):
        if mtl and stac or (not mtl and not stac):
            print("Please choose one of either MTL or STAC, not both")
            sys.exit(1)

        item = None
        if mtl:
            # Transform not implemented, so tell folks
            print("MTL transform not yet implemented.")
            sys.exit(1)
            with open(mtl) as f:
                item = transform_mtl_to_stac(json.load(f))
        elif stac:
            in_item = Item.from_file(stac)
            item = transform_stac_to_stac(in_item, enable_proj=enable_proj)

        item_path = os.path.join(dst, '{}.json'.format(item.id))
        item.set_self_href(item_path)

        item.save_object()

    return landsat_command
