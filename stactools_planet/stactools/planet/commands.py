import logging

import click
import pystac

from stactools import core
from stactools.planet import OrderManifest

logger = logging.getLogger(__name__)


def convert_order(manifest,
                  destination,
                  collection_id,
                  move_assets=False,
                  copy=False,
                  description=None,
                  title=None,
                  skip_validation=False,
                  catalog_type=pystac.CatalogType.SELF_CONTAINED):
    manifest = OrderManifest.from_file(manifest)
    collection = manifest.to_stac(collection_id=collection_id,
                                  description=description,
                                  title=title)
    collection.normalize_hrefs(destination)

    if not skip_validation:
        collection.validate_all()

    logger.info('Saving STAC collection at {}...'.format(
        collection.get_self_href()))
    collection.save(catalog_type=catalog_type)

    # Move assets after save to avoid moving without saving,
    # and so the directory structure is generated.
    if move_assets:
        logger.info('Moving assets into STAC...')
        collection = core.move_all_assets(collection, copy=copy)
        collection.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)


def create_planet_command(cli):
    """Creates a command group for commands dealing with Planet data
    """
    @cli.group('planet', short_help="Commands for working with Planet data")
    def planet():
        pass

    @planet.command('convert-order',
                    short_help='Convert Planet Order data to STAC Collection')
    @click.argument('manifest')
    @click.argument('destination')
    @click.argument('id')
    @click.argument('description')
    @click.option(
        '-a',
        '--assets',
        type=click.Choice(['move', 'copy'], case_sensitive=False),
        help='Move or copy asset files alongside the STAC Item locations.')
    @click.option('-t',
                  '--title',
                  help='Optional title for the STAC collection.')
    @click.option('--skip-validation', help='Skip validation on the STAC')
    @click.option('-c',
                  '--catalog-type',
                  type=click.Choice([
                      pystac.CatalogType.ABSOLUTE_PUBLISHED,
                      pystac.CatalogType.RELATIVE_PUBLISHED,
                      pystac.CatalogType.SELF_CONTAINED
                  ],
                                    case_sensitive=False),
                  default=pystac.CatalogType.SELF_CONTAINED)
    def convert_command(manifest, destination, id, assets, description, title,
                        skip_validation, catalog_type):
        """Converts a planet order to a STAC Catalog.

        The Planet order is passed in via the manifest.json file located at
        MANIFEST. The DESTINATION is a directory that you want the STAC to be located.
        The STAC created will have an id determined by ID and a
        description supplied with DESCRIPTION.
        """
        convert_order(manifest,
                      destination,
                      collection_id=id,
                      move_assets=assets is not None,
                      copy=(assets == 'copy'),
                      description=description,
                      title=title,
                      skip_validation=skip_validation,
                      catalog_type=catalog_type)

    return planet
