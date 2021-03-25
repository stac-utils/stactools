import logging
import os

import click

from stactools.cgls_lc100 import stac, cog

logger = logging.getLogger(__name__)


def create_cgls_lc100_command(cli):
    """Creates a command group for commands working with
    Copernicus Global Land Cover Layers data.
    """
    @cli.group('cgls_lc100',
               short_help=("Commands for working with "
                           "Copernicus Global Land Cover Layers data."))
    def cgls_lc100():
        pass

    @cgls_lc100.command('create-item',
                        short_help=("Create a STAC Item from a Copernicus "
                                    "Global Land Cover Layers tif file."))
    @click.argument('tif_href')
    @click.argument('dst')
    @click.option('-c',
                  '--cogify',
                  is_flag=True,
                  help='Convert the tif into COG.')
    def create_item_command(tif_href, dst, cogify):
        """Creates a STAC Item based on metadata from a tif
        Copernicus Global Land Cover Layers file.

        TIF_REF is the Copernicus Global Land Cover Layers tif file.
        DST is directory that a STAC Item JSON file will be created
        in. This will have a filename that matches the ID, which will
        is the name of the tif_REF, without it's file extension.
        """

        item = stac.create_item(tif_href)

        item_path = os.path.join(dst, '{}.json'.format(item.id))
        item.set_self_href(item_path)

        if cogify:
            cog.create_cogs(item)

        item.save_object()

    return cgls_lc100
