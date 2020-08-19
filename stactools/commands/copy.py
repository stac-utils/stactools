import click
import pystac


def copy(src, dst, catalog_type, copy_assets=False):
    print('copy {} {} {} {}'.format(src, dst, catalog_type, copy_assets))
    # TODO
    # cat = pystac.read_file(src)
    # cat.normalize_and_save(dst, catalog_type)


def create_copy_command(cli):
    @cli.command('copy', short_help='Copy a STAC Catalog')
    @click.argument('src')
    @click.argument('dst')
    @click.argument('catalog_type',
                    type=click.Choice([
                        pystac.CatalogType.ABSOLUTE_PUBLISHED,
                        pystac.CatalogType.RELATIVE_PUBLISHED,
                        pystac.CatalogType.SELF_CONTAINED
                    ],
                                      case_sensitive=False))
    @click.option('--copy_assets', '-a', is_flag=True)
    def copy_command(src, dst, catalog_type, copy_assets):
        copy(src, dst, catalog_type, copy_assets)

    return copy_command
