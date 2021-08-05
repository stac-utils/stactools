import click
import pystac

from typing import Optional
from stactools.core import merge_all_items


def merge(source_catalog: str,
          target_catalog: str,
          collection_id: Optional[str] = None,
          move_assets: bool = False,
          ignore_conflicts: bool = False,
          as_child: bool = False,
          child_folder: Optional[str] = None) -> None:
    source = pystac.read_file(source_catalog)
    if not isinstance(source, pystac.Catalog):
        raise click.BadArgumentUsage(f"{source_catalog} is not a STAC Catalog")

    target = pystac.read_file(target_catalog)
    if not isinstance(target, pystac.Catalog):
        raise click.BadArgumentUsage(f"{target_catalog} is not a STAC Catalog")

    if collection_id is not None:
        target_new = target.get_child(collection_id, recursive=True)
        if target_new is None:
            raise click.BadOptionUsage(
                'collection',
                'A collection with ID {} does not exist in {}'.format(
                    collection_id, target_catalog))
        target = target_new
    merge_all_items(source, target, move_assets, ignore_conflicts, as_child,
                    child_folder)

    target.save()


def create_merge_command(cli: click.Group) -> click.Command:
    @cli.command('merge', short_help='Merge items from one STAC into another.')
    @click.argument('source_catalog')
    @click.argument('target_catalog')
    @click.option('--collection',
                  help=("The collection ID to merge into. If not set, will "
                        "merge into the root catalog or collection."))
    @click.option('-a',
                  '--move-assets',
                  is_flag=True,
                  help='Move assets to the target catalog Item locations.')
    @click.option(
        '--ignore-conflicts',
        is_flag=True,
        help=('If there are conflicts with an item in both catalogs having '
              'the same asset key, do not error, leave the original asset '
              'from the target catalog in place.'))
    @click.option(
        '-c',
        '--as-child',
        is_flag=True,
        help='Merge as child catalog of destination catalog or collection')
    @click.option('-f',
                  '--child-folder',
                  help=('The subfolder name to copy to if the option to merge '
                        'as a child is used. If not provided, the catalog id '
                        'will be used'))
    def merge_command(source_catalog: str, target_catalog: str,
                      collection: str, move_assets: bool,
                      ignore_conflicts: bool, as_child: bool,
                      child_folder: str) -> None:
        merge(source_catalog,
              target_catalog,
              collection_id=collection,
              move_assets=move_assets,
              ignore_conflicts=ignore_conflicts,
              as_child=as_child,
              child_folder=child_folder)

    return merge_command
