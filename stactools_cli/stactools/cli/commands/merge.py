import click
import pystac

from stactools.core import merge_all_items


def merge(source_catalog,
          target_catalog,
          collection_id=None,
          move_assets=False,
          ignore_conflicts=False):
    source = pystac.read_file(source_catalog)
    target = pystac.read_file(target_catalog)

    if collection_id is not None:
        target = target.get_child(collection_id, recursive=True)
        if target is None:
            raise click.BadOptionUsage(
                'collection',
                'A collection with ID {} does not exist in {}'.format(
                    collection_id, target_catalog))

    merge_all_items(source, target, move_assets, ignore_conflicts)

    target.save()


def create_merge_command(cli):
    @cli.command('merge', short_help='Merge items from one STAC into another.')
    @click.argument('source_catalog')
    @click.argument('target_catalog')
    @click.option('-c',
                  '--collection',
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
    def merge_command(source_catalog, target_catalog, collection, move_assets,
                      ignore_conflicts):
        merge(source_catalog,
              target_catalog,
              collection_id=collection,
              move_assets=move_assets,
              ignore_conflicts=ignore_conflicts)

    return merge_command
