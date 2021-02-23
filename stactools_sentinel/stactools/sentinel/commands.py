import os
import logging
import click
import json

from stactools.sentinel.stac import create_item
from stactools.sentinel.cog import create_cogs

logger = logging.getLogger(__name__)


def create_sentinel_command(cli):
    @cli.group('sentinel',
               short_help=("Commands for working with sentinel data"))
    def sentinel():
        pass

    @sentinel.command(
        'create-item',
        short_help='Convert a Sentinel2 L2A granule into a STAC item')
    @click.argument('src')
    @click.argument('dst')
    @click.option(
        '-p',
        '--providers',
        help='Path to JSON file containing array of additional providers')
    @click.option('-c',
                  '--cogify',
                  is_flag=True,
                  help='Convert each non-COG asset into a COG')
    def create_item_command(src, dst, providers, cogify):
        """Creates a STAC Item for a given Sentinel 2 granule

        SRC is the path to the granule
        DST is directory that a STAC Item JSON file will be created
        in. This will have a filename that matches the ID, which will
        be derived from the Sentinel 2 metadata.
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

    return sentinel
