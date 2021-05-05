import click
import pystac

from stactools.core import layout_catalog


def create_layout_command(cli):
    @cli.command(
        'layout',
        short_help='Reformat the layout of a STAC based on templating.')
    @click.argument('catalog')
    @click.argument('item_path_template')
    @click.option(
        '-s',
        '--create-subcatalogs',
        is_flag=True,
        help=('Create subcatalogs based on the template values instead of '
              'just creating directories.'))
    @click.option(
        '-k',
        '--remove-existing-subcatalogs',
        is_flag=True,
        help=('If this flag is set, existing subcatalogs will be'
              'removed. If --create_subcatalogs is used, all items'
              'will be places in the new subcatalogs from the source_catalog.')
    )
    @click.option('-a',
                  '--move-assets',
                  is_flag=True,
                  help='Move assets to the target catalog Item locations.')
    def layout_command(catalog, item_path_template, create_subcatalogs,
                       remove_existing_subcatalogs, move_assets):
        source = pystac.read_file(catalog)

        layout_catalog(source,
                       item_path_template,
                       create_subcatalogs=create_subcatalogs,
                       remove_existing_subcatalogs=remove_existing_subcatalogs,
                       move_assets=move_assets)

        source.save()

    return layout_command
