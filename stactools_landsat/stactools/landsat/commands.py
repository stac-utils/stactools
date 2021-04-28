import os

import click
import pystac

from stactools.landsat.utils import transform_stac_to_stac
from stactools.landsat.stac import create_stac_item


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

    @landsat.command(
        "create-item",
        short_help="Create a STAC item from collection 2 scene metadata.")
    @click.option("--level",
                  type=click.Choice(['level-1', 'level-2'],
                                    case_sensitive=False),
                  default="level-2",
                  show_default=True,
                  help="Product level to process")
    @click.option("--mtl", required=True, help="HREF to an MTL file.")
    @click.option("--output",
                  required=True,
                  help="HREF of diretory in which to write the item.")
    def create_item_cmd(level: str, mtl: str, output: str):
        """Creates a STAC Item for a Landsat 8 C2 Level-2 scene's products.

        All asset paths are based on the MTL path, as all assets are assumed to
        reside in the same directory/blob prefix/etc.
        """
        if level != 'level-2':
            raise click.BadOptionUsage("level",
                                       "Only level-2 currently implemented.")

        item = create_stac_item(mtl_xml_href=mtl)
        item.set_self_href(os.path.join(output, f'{item.id}.json'))
        item.save_object()

    @landsat.command(
        "convert",
        short_help="Convert a USGS STAC 0.7 Item to an updated STAC Item")
    @click.option("--stac", "-s", required=True, help="Path to a STAC file.")
    @click.option(
        "--enable-proj",
        "-p",
        is_flag=True,
        help="Enable the proj extension. Requires access to blue band.")
    @click.option("--dst", "-d", help="Output directory")
    def convert_cmd(stac, enable_proj, dst):
        in_item = pystac.Item.from_file(stac)
        item = transform_stac_to_stac(in_item, enable_proj=enable_proj)

        item_path = os.path.join(dst, '{}.json'.format(item.id))
        item.set_self_href(item_path)
        item.save_object()

    return landsat
