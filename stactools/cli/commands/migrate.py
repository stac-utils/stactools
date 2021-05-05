import click


def migrate(option):
    # TODO
    print(option)


def create_migrate_command(cli):
    @cli.command('migrate', short_help='Migrate a STAC catalog (TODO)')
    @click.option('--option', '-o', default=1, help='A test option')
    def migrate_command(option):
        migrate(option)

    return migrate_command
