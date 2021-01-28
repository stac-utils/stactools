import logging
import click

from stactools.sentinel.stac import create_item

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
    # @click.argument('dst')

    @click.option(
        '-p',
        '--providers',
        help='Path to JSON file containing array of additional providers')
    def create_item_command(src, providers):
        additional_providers = None
        if providers is not None:
            with open(providers) as f:
                additional_providers = json.load(f)

        create_item(src, additional_providers=additional_providers)
        # item = create_item(src, additional_providers=additional_providers)
        # item_path = os.path.join(dst, '{}.json'.format(item.id))
        # item.set_self_href(item_path)

        # item.save_object()

    return sentinel
