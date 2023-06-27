import click
from stactools.core import migrate_object


def create_migrate_command(cli: click.Group) -> click.Command:
    @cli.command("migrate", short_help="Migrate a STAC object")
    @click.argument("href")
    @click.option(
        "-s",
        "--save",
        is_flag=True,
        help="Save migrated STAC object in original location.",
    )
    @click.option(
        "--show-diff/--hide-diff",
        default=True,
        help=(
            "Whether to dump diff between original and migrated object to stdout. "
            "Defaults to --show-diff. "
        ),
    )
    def migrate_command(href: str, save: bool, show_diff: bool) -> None:
        migrate_object(href, save=save, show_diff=show_diff)

    return migrate_command
