import click
import pystac
from stactools.core import add_raster_to_item


def add_raster(item_path: str) -> None:
    item = pystac.read_file(item_path)
    if not isinstance(item, pystac.Item):
        raise click.BadArgumentUsage(f"{item_path} is not a STAC Item")
    item = add_raster_to_item(item)
    item.save_object()


def create_add_raster_command(cli: click.Group) -> click.Command:
    @cli.command("add-raster", short_help="Add raster extension to an Item.")
    @click.argument("item_path")
    def add_raster_command(item_path: str) -> None:
        add_raster(item_path)

    return add_raster_command
