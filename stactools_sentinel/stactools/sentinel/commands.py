import logging
import click

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
    @click.option('-c', '--cogify')
    def create_item_command(cli):
        pass

    return sentinel
