import click
import pystac


def print_info(catalog_path: str) -> None:
    cat_count, col_count, item_count = 0, 0, 0
    cat_ext, col_ext, item_ext = set([]), set([]), set([])

    cat = pystac.read_file(catalog_path)
    if not isinstance(cat, pystac.Catalog):
        print("{} is not a catalog".format(catalog_path))
        return

    for root, _, items in cat.walk():
        if root.STAC_OBJECT_TYPE == pystac.STACObjectType.COLLECTION:
            col_count += 1
            if root.stac_extensions is not None:
                for ext in root.stac_extensions:
                    col_ext.add(ext)
        else:
            cat_count += 1
            if root.stac_extensions is not None:
                for ext in root.stac_extensions:
                    cat_ext.add(ext)

        for item in items:
            item_count += 1
            if item.stac_extensions is not None:
                for ext in item.stac_extensions:
                    item_ext.add(ext)

    cat_id_info = 'Catalog ID: {}'.format(cat.id)
    cat_ext_info = '(extensions: {})'.format(
        ','.join(cat_ext)) if cat_ext else ''
    col_ext_info = '(extensions: {})'.format(
        ','.join(col_ext)) if col_ext else ''
    item_ext_info = '(extensions: {})'.format(
        ','.join(item_ext)) if item_ext else ''

    print(cat_id_info)
    print('-' * len(cat_id_info))
    print('   CATALOGS: {} {}'.format(cat_count, cat_ext_info))
    print('COLLECTIONS: {} {}'.format(col_count, col_ext_info))
    print('      ITEMS: {} {}'.format(item_count, item_ext_info))


def create_info_command(cli: click.Group) -> click.Command:

    @cli.command('info',
                 short_help='Display info about a static STAC catalog.')
    @click.argument('catalog_path')
    def info_command(catalog_path: str) -> None:
        print_info(catalog_path)

    return info_command


def create_describe_command(cli: click.Group) -> click.Command:

    @cli.command(
        'describe',
        short_help='Prints out a list of all catalogs, collections and items '
        'in this STAC.')
    @click.argument('catalog_path')
    @click.option('-h',
                  '--include-hrefs',
                  is_flag=True,
                  help='Include HREFs in description.')
    def describe_command(catalog_path: str, include_hrefs: bool) -> None:
        cat = pystac.read_file(catalog_path)
        if not isinstance(cat, pystac.Catalog):
            print("{} is not a catalog".format(catalog_path))
            return
        cat.describe(include_hrefs=include_hrefs)

    return describe_command
