import logging
import json
import os

import click
import pystac

from stactools.naip.stac import create_item

logger = logging.getLogger(__name__)


def create_naip_command(cli):
    """Creates a command group for commands working with
    NAIP imagery.
    """
    @cli.group('naip',
               short_help=("Commands for working with "
                           "NAIP imagery."))
    def naip():
        pass

    @naip.command('create-item',
                  short_help='Create a STAC Item from NAIP imagery data')
    @click.argument('state')
    @click.argument('year')
    @click.argument('cog_href')
    @click.argument('dst')
    @click.option('-f', '--fgdc', help='HREF to FGDC metadata.')
    @click.option('-t',
                  '--thumbnail',
                  help='HREF to the thumbnail for this NAIP tile')
    @click.option(
        '-p',
        '--providers',
        help='Path to JSON file containing array of additional providers')
    def create_item_command(state, year, cog_href, dst, fgdc, thumbnail,
                            providers):
        """Creates a STAC Item based on metadata from a NAIP tile.

        STATE is the state this NAIP tile belongs to.
        COG_HREF is the href to the COG that is the NAIP tile.
        FGDC_HREF is href to the text metadata file in the NAIP fgdc format.
        DST is directory that a STAC Item JSON file will be created
        in.
        """
        additional_providers = None
        if providers is not None:
            with open(providers) as f:
                additional_providers = [
                    pystac.Provider.from_dict(d) for d in json.load(f)
                ]

        item = create_item(state,
                           year,
                           cog_href,
                           fgdc_metadata_href=fgdc,
                           thumbnail_href=thumbnail,
                           additional_providers=additional_providers)

        item_path = os.path.join(dst, '{}.json'.format(item.id))
        item.set_self_href(item_path)

        item.save_object()

    return naip
