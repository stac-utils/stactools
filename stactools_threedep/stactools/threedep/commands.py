import click
import os.path

from pystac import Catalog, Collection, Extent, CatalogType, STAC_IO

from stactools.threedep.constants import (PRODUCTS, DESCRIPTION, USGS_PROVIDER,
                                          USGS_FTP_BASE, USGS_3DEP_ID)
from stactools.threedep import utils, stac


def create_threedep_command(cli):
    """Creates the threedep command line utility."""
    @cli.group("threedep", short_help="Work with USGS 3DEP elevation data.")
    def threedep():
        pass

    @threedep.command(
        "create-collection",
        short_help="Create a STAC collection for existing USGS 3DEP data")
    @click.argument("destination")
    @click.option("-s",
                  "--source",
                  help="The href of a directory tree containing metadata",
                  default=None)
    @click.option("-i",
                  "--id",
                  multiple=True,
                  help="Ids to fetch. If not provided, will fetch all IDs.")
    @click.option("--quiet/--no-quiet", default=False)
    def create_collection_command(destination, source, id, quiet):
        """Creates a 3DEP collection in DESTINATION.

        If SOURCE is not provided, will use the metadata in USGS. SOURCE is
        expected to be a directory tree mirroring the structure on USGS, so
        it is best created using `stac threedep download-metadata`.
        """
        base_ids = id  # not sure how to rename arguments in click
        items = {}
        for product in PRODUCTS:
            items[product] = []
            if base_ids:
                ids = base_ids
            else:
                ids = utils.fetch_ids(product)
            for id in ids:
                item = stac.create_item(product, id, source)
                items[product].append(item)
                if not quiet:
                    print(item.id)
        all_items = [item for sublist in items.values() for item in sublist]
        if not all_items:
            raise Exception("no items found")
        extent = Extent.from_items(all_items)
        collection = Collection(
            id=USGS_3DEP_ID,
            title="USGS 3DEP DEMs",
            keywords=["USGS", "3DEP", "NED", "DEM", "elevation"],
            providers=[USGS_PROVIDER],
            description=DESCRIPTION,
            extent=extent,
            license="PDDL-1.0")
        for product in PRODUCTS:
            if product == "1":
                title = "1 arc-second"
                description = "USGS 3DEP 1 arc-second DEMs"
            elif product == "13":
                title = "1/3 arc-second"
                description = "USGS 3DEP 1/3 arc-second DEMs"
            else:
                raise NotImplementedError
            catalog = Catalog(id=product, description=description, title=title)
            collection.add_child(catalog)
            catalog.add_items(items[product])
        collection.update_extent_from_items()
        collection.normalize_hrefs(destination)
        collection.save(catalog_type=CatalogType.SELF_CONTAINED)
        collection.validate()

    @threedep.command("download-metadata",
                      short_help="Download all metadata for USGS 3DEP data")
    @click.argument("destination")
    @click.option("-i",
                  "--id",
                  multiple=True,
                  help="Ids to fetch. If not provided, will fetch all IDs.")
    @click.option("--quiet/--no-quiet", default=False)
    def download_metadata_command(destination, id, quiet):
        """Creates a 3DEP collection in DESTINATION."""
        base_ids = id  # not sure how to rename arguments in click
        for product in PRODUCTS:
            if base_ids:
                ids = base_ids
            else:
                ids = utils.fetch_ids(product)
            for id in ids:
                path = utils.path(product,
                                  id,
                                  extension="xml",
                                  base=destination)
                if os.path.exists(path):
                    if not quiet:
                        print("{} exists, skipping download...".format(path))
                    continue
                os.makedirs(os.path.dirname(path), exist_ok=True)
                source_path = utils.path(product,
                                         id,
                                         extension="xml",
                                         base=USGS_FTP_BASE)
                if not quiet:
                    print("{} -> {}".format(source_path, path))
                text = STAC_IO.read_text(source_path)
                with open(path, "w") as f:
                    f.write(text)
