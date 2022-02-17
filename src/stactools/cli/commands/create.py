import click

from stactools.core import create


def create_create_item_command(cli: click.Group) -> click.Command:

    @cli.command('create-item', short_help='Creates an item from an asset')
    @click.argument('href')
    def create_item_command(href: str) -> None:
        """Creates an Item from a href.

        The href must be a `rasterio` readable asset. The item's dictionary will
        be printed to stdout. This item is intentinonally _extremely_ minimal.
        If you need additional capabilities, we recommend using [rio
        stac](https://github.com/developmentseed/rio-stac/).
        """
        item = create.item(href)
        print(item.to_dict())

    return create_item_command
