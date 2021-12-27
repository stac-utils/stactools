import click

from typing import Optional

from pystac import Catalog, Item, read_file

from stactools.core import add_item


def add(source_item: str,
        target_catalog: str,
        collection_id: Optional[str] = None,
        move_assets: bool = False) -> None:
    source = read_file(source_item)
    if not isinstance(source, Item):
        raise click.BadArgumentUsage(f"{source_item} is not a STAC Item")
    target = read_file(target_catalog)
    if not isinstance(target, Catalog):
        raise click.BadArgumentUsage(f"{target_catalog} is not a STAC Catalog")

    if collection_id is not None:
        target_collection = target.get_child(collection_id, recursive=True)
        if target_collection is None:
            raise click.BadOptionUsage(
                'collection',
                'A collection with ID {} does not exist in {}'.format(
                    collection_id, target_catalog))

        add_item(source, target_collection, move_assets)
        target_collection.save()
    else:
        add_item(source, target, move_assets)
        target.save()


def create_add_command(cli: click.Group) -> click.Command:

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
    def add_command(source_item: str, target_catalog: str, collection: str,
                    move_assets: bool) -> None:
        add(source_item,
            target_catalog,
            collection_id=collection,
            move_assets=move_assets)

    return add_command
