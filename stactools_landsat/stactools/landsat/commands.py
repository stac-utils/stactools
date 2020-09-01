import click


def convert_mtl_to_item(mtl, dst):
    print('LANDSAT CONVERT {} {}'.format(mtl, st))


def create_convert_command(cli):
    @cli.command('landsat-convert',
                 short_help='Convert a Landsat MTL file to a STAC Item (TODO)')
    @click.argument('mlt')
    @click.argument('dst')
    def convert_command(mlt, dst):
        convert_mlt_to_item(src, dst)

    return convert_command
