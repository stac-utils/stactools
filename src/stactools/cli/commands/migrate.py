import click


def migrate(option: click.Option) -> None:
    # TODO
    print(option)


def create_migrate_command(cli: click.Group) -> click.Command:

    @cli.command('migrate', short_help='Migrate a STAC catalog (TODO)')
    @click.option('--option', '-o', default=1, help='A test option')
    def migrate_command(option: click.Option) -> None:
        migrate(option)

    return migrate_command
