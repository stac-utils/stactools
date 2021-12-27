import click
import pystac

from typing import Optional
from pystac.utils import make_absolute_href
from stactools.core.copy import copy_catalog, move_all_assets


def create_move_assets_command(cli: click.Group) -> click.Command:

    @cli.command(
        'move-assets',
        short_help='Move or copy assets in a STAC to the Item locations.')
    @click.argument('catalog_path')
    @click.option('-c',
                  '--copy',
                  help='Copy assets instead of moving.',
                  is_flag=True)
    @click.option('-s',
                  '--asset-subdirectory',
                  help=('Subdirectory to place assets '
                        'inside of the directory containing '
                        'their items'))
    def move_assets_command(catalog_path: str, copy: bool,
                            asset_subdirectory: str) -> None:
        """Move or copy assets in a STAC Catalog.

        For all assets in the catalog at CATALOG_PATH, move or copy
        those assets into the directory of the item for which they belong.
        If --asset-subdirectory is used, moves them instead into a directory
        called 'assets' next to the item for which they belong. If -c is used,
        assets are copied; otherwise they are moved.

        Note: If the catalog is an ABSOLUTE_PUBLISHED catalog, the assets will have
        an absolute HREF after this operation. Otherwise, it will have a relative HREF.
        """
        catalog = pystac.read_file(catalog_path)
        if not isinstance(catalog, pystac.Catalog):
            raise click.BadArgumentUsage(
                f"{catalog_path} is not a STAC Catalog")

        processed = move_all_assets(catalog,
                                    asset_subdirectory=asset_subdirectory,
                                    copy=copy)

        processed.save()

    return move_assets_command


def create_copy_command(cli: click.Group) -> click.Command:

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
    @click.option('-l',
                  '--publish-location',
                  help=('Location to use for resolving HREF links '
                        'instead of the destination folder.'))
    def copy_command(src: str, dst: str, catalog_type: pystac.CatalogType,
                     copy_assets: bool,
                     publish_location: Optional[str]) -> None:
        """Copy a STAC Catalog or Collection at SRC to the directory
        at DST.

        Note: Copying a catalog will upgrade it to the latest version of STAC."""
        source_catalog = pystac.read_file(make_absolute_href(src))
        if not isinstance(source_catalog, pystac.Catalog):
            raise click.BadArgumentUsage(f"{src} is not a STAC Catalog")
        copy_catalog(source_catalog, dst, catalog_type, copy_assets,
                     publish_location)

    return copy_command
