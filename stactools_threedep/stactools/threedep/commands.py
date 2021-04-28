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
        "create-catalog",
        short_help="Create a STAC catalog for existing USGS 3DEP data")
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
    def create_catalog_command(destination, source, id, quiet):
        """Creates a relative published 3DEP catalog in DESTINATION.

        If SOURCE is not provided, will use the metadata in AWS. SOURCE is
        expected to be a directory tree mirroring the structure on USGS, so
        it is best created using `stac threedep download-metadata`.
        """
        base_ids = id  # not sure how to rename arguments in click
        collections = {}
        items = {}
        for product in PRODUCTS:
            items[product] = []
            if base_ids:
                ids = base_ids
            else:
                ids = utils.fetch_ids(product)
            for id in ids:
                item = stac.create_item_from_product_and_id(
                    product, id, source)
                items[product].append(item)
                if not quiet:
                    print(item.id)
            extent = Extent.from_items(items[product])
            if product == "1":
                title = "1 arc-second"
                description = "USGS 3DEP 1 arc-second DEMs"
            elif product == "13":
                title = "1/3 arc-second"
                description = "USGS 3DEP 1/3 arc-second DEMs"
            else:
                raise NotImplementedError
            collection = Collection(
                id=f"{USGS_3DEP_ID}-{product}",
                title=title,
                keywords=["USGS", "3DEP", "NED", "DEM", "elevation"],
                providers=[USGS_PROVIDER],
                description=description,
                extent=extent,
                license="PDDL-1.0")
            collections[product] = collection
        catalog = Catalog(id=USGS_3DEP_ID,
                          description=DESCRIPTION,
                          title="USGS 3DEP DEMs",
                          catalog_type=CatalogType.RELATIVE_PUBLISHED)
        for product, collection in collections.items():
            catalog.add_child(collection)
            collection.add_items(items[product])
        catalog.generate_subcatalogs("${threedep:region}")
        catalog.normalize_hrefs(destination)
        catalog.save()
        catalog.validate()

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

    @threedep.command(
        "fetch-ids",
        short_help="Fetch all product ids and print them to stdout")
    @click.argument("product")
    @click.option("--usgs-ftp/--no-usgs-ftp",
                  default=False,
                  help="Fetch from the USGS FTP instead of AWS.")
    def fetch_ids_command(product: str, usgs_ftp: bool):
        """Fetches product ids and prints them to stdout."""
        for id in utils.fetch_ids(product, use_usgs_ftp=usgs_ftp):
            print(id)
