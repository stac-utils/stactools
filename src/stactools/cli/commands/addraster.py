import click
import pystac
from stactools.core import add_raster_to_item


def add_raster(item_path: str) -> None:
    item = pystac.read_file(item_path)
    if not isinstance(item, pystac.Item):
        raise click.BadArgumentUsage(f"{item_path} is not a STAC Item")
    item = add_raster_to_item(item)
    item.save_object()


def create_addraster_command(cli: click.Group) -> click.Command:

    @cli.command("addraster", short_help="Add raster extension to an Item.")
    @click.argument("item_path")
    def addraster_command(item_path: str) -> None:
        add_raster(item_path)

    return addraster_command
