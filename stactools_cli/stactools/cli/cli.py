import click

from stactools.cli import registry


@click.group()
def cli():
    pass


for create_subcommand in registry.get_create_subcommand_functions():
    create_subcommand(cli)


def run_cli():
    cli(prog_name='stactools')


if __name__ == "__main__":
    run_cli()
