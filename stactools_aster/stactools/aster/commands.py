import logging
import json
import os

import click

from stactools.aster.stac import create_item
from stactools.aster.cog import create_cogs

logger = logging.getLogger(__name__)


def create_aster_command(cli):
    """Creates a command group for commands working with
    ASTER L1T Radiance Version 003 data.
    """
    @cli.group('aster',
               short_help=("Commands for working with "
                           "ASTER L1T Radiance Version 003 data."))
    def aster():
        pass

    @aster.command('create-item',
                   short_help='Create an ASTER  HDF file into a STAC Item')
    @click.argument('src')
    @click.argument('dst')
    @click.option('-c',
                  '--cogify',
                  is_flag=True,
                  help='Convert the HDF into a set of COGs.')
    @click.option(
        '-p',
        '--providers',
        help='Path to JSON file containing array of additional providers')
    def create_item_command(src, dst, cogify, providers):
        """Creates a STAC Item based on metadata from an HDF-EOS
        ASTER L1T Radiance Version 003 file.

        SRC is th HDF-EOS ASTER L1T 003 file.
        DST is directory that a STAC Item JSON file will be created
        in. This will have a filename that matches the ID, which will
        be derived from the SRC file name.
        """
        additional_providers = None
        if providers is not None:
            with open(providers) as f:
                additional_providers = json.load(f)

        item = create_item(src, additional_providers=additional_providers)

        item_path = os.path.join(dst, '{}.json'.format(item.id))
        item.set_self_href(item_path)

        if cogify:
            create_cogs(item)

        item.save_object()

    return aster
