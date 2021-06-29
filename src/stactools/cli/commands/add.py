import click
import pystac

from stactools.core import add_item


def add(source_item, target_catalog, collection_id=None, move_assets=False):
    source = pystac.read_file(source_item)
    target = pystac.read_file(target_catalog)

    if collection_id is not None:
        target = target.get_child(collection_id, recursive=True)
        if target is None:
            raise click.BadOptionUsage(
                'collection',
                'A collection with ID {} does not exist in {}'.format(
                    collection_id, target_catalog))

    add_item(source, target, move_assets)

    target.save()


def create_add_command(cli):
    @cli.command('add', short_help='Add an item to a catalog/collection.')
    @click.argument('source_item')
    @click.argument('target_catalog')
    @click.option('--collection',
                  help=("The collection ID to add to. If not set, will "
                        "add to the root catalog or collection."))
    @click.option('-a',
                  '--move-assets',
                  is_flag=True,
                  help='Move assets to the target catalog Item locations.')
    def add_command(source_item, target_catalog, collection, move_assets):
        add(source_item,
            target_catalog,
            collection_id=collection,
            move_assets=move_assets)

    return add_command
