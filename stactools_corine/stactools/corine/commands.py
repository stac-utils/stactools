import logging
import os

import click

from stactools.corine import stac, cog

logger = logging.getLogger(__name__)


def create_corine_command(cli):
    """Creates a command group for commands working with
    CORINE Land Cover data.
    """
    @cli.group('corine',
               short_help=("Commands for working with "
                           "CORINE Land Cover data."))
    def corine():
        pass

    @corine.command('create-item',
                    short_help='Create a STAC Item from a CORINE metadata file'
                    )
    @click.argument('metadata_href')
    @click.argument('dst')
    @click.option('-c',
                  '--cogify',
                  is_flag=True,
                  help='Convert the tif into COG.')
    def create_item_command(metadata_href, dst, cogify):
        """Creates a STAC Item based on metadata from an tif
        CORINE Land Cover file.

        METADATA_REF is the CORINE Land Cover metadata file. The
        tif file will be located in the same directory as that of METADATA_REF.
        DST is directory that a STAC Item JSON file will be created
        in. This will have a filename that matches the ID, which will
        is the name of the METADATA_REF, without it's file extension.
        """

        item = stac.create_item(metadata_href)

        item_path = os.path.join(dst, '{}.json'.format(item.id))
        item.set_self_href(item_path)

        if cogify:
            cog.create_cogs(item)

        item.save_object()

    return corine
