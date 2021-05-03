from stactools.goes.dataset import Dataset
import click
import os.path

from stactools.goes import stac


def create_goes_command(cli):
    @cli.group("goes", short_help="Command for working with GOES data")
    def goes():
        pass

    @goes.command("create-item",
                  short_help="Creates a STAC item from a GOES netcdf file")
    @click.argument("href")
    @click.argument("destination")
    @click.option("-c",
                  "--cogify",
                  is_flag=True,
                  help="Convert the netcdf to two COGs")
    @click.option("--tight-geometry/--no-tight-geometry", default=True)
    def create_item(href, destination, cogify, tight_geometry):
        """Creates a STAC item from a GOES netcdf file.

        If `--cogify` is provided, will produce two COGs, one for the data and
        one for the data quality field.
        """
        dataset = Dataset(href, tight_geometry)
        if cogify:
            cogs = dataset.cogify(destination)
        else:
            cogs = {}
        item = stac.create_item_from_dataset(dataset, cogs=cogs)
        path = os.path.join(destination, f"{item.id}.json")
        item.set_self_href(path)
        item.validate()
        item.save_object()

    return goes
