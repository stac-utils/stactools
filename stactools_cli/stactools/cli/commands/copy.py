import click
import pystac

from stactools.core.copy import copy_catalog, move_all_assets


def create_move_assets_command(cli):
    @cli.command(
        'move-assets',
        short_help='Move or copy assets in a STAC to the Item locations.')
    @click.argument('catalog_path')
    @click.option('-c', '--copy', help='Copy assets instead of moving.')
    @click.option('-s',
                  '--asset-subdirectory',
                  help=('Subdirectory to place assets '
                        'inside of the directory containing '
                        'their items'))
    @click.option(
        '-h',
        '--href-type',
        type=click.Choice([pystac.LinkType.ABSOLUTE, pystac.LinkType.RELATIVE],
                          case_sensitive=False),
        help=('If supplied, forces asset HREFs to be either absolute or '
              'relative HREFS'))
    def move_assets_command(catalog_path, copy, asset_subdirectory, href_type):
        catalog = pystac.read_file(catalog_path)
        move_all_assets(catalog,
                        asset_subdirectory=asset_subdirectory,
                        href_type=href_type,
                        copy=copy)

    return move_assets_command


def create_copy_command(cli):
    @cli.command('copy', short_help='Copy a STAC Catalog')
    @click.argument('src')
    @click.argument('dst')
    @click.option('-t',
                  '--catalog-type',
                  type=click.Choice([
                      pystac.CatalogType.ABSOLUTE_PUBLISHED,
                      pystac.CatalogType.RELATIVE_PUBLISHED,
                      pystac.CatalogType.SELF_CONTAINED
                  ],
                                    case_sensitive=False))
    @click.option('--copy-assets',
                  '-a',
                  is_flag=True,
                  help=('Copy all item assets to '
                        'be alongside the new item location.'))
    def copy_command(src, dst, catalog_type, copy_assets):
        """Copy a STAC Catalog or Collection at SRC to the directory
        at DST.

        Note: Copying a catalog will upgrade it to the latest version of STAC."""
        source_catalog = pystac.read_file(src)
        copy_catalog(source_catalog, dst, catalog_type, copy_assets)

    return copy_command
