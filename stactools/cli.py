import click

from stactools.commands.copy import create_copy_command
from stactools.commands.migrate import create_migrate_command


@click.group()
def cli():
    pass


copy_command = create_copy_command(cli)
migrate_command = create_migrate_command(cli)

if __name__ == "__main__":
    cli()
