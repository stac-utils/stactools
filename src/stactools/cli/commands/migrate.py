import click
import pystac
from stactools.core import migrate_object


def _migrate(
    href: str, save: bool = False, recursive: bool = False, show_diff: bool = True
) -> pystac.STACObject:
    if save is False and show_diff is False:
        raise click.BadArgumentUsage(
            "It is only valid to use 'hide-diff' when 'save' is enabled "
            "otherwise there would be no output."
        )

    stac_object = pystac.read_file(href)
    if recursive and not isinstance(stac_object, (pystac.Catalog, pystac.Collection)):
        raise click.BadArgumentUsage(
            "'recursive' is only a valid option for "
            "pystac.Catalogs and pystac.Collections"
        )
    return migrate_object(
        stac_object, save=save, recursive=recursive, show_diff=show_diff
    )


def create_migrate_command(cli: click.Group) -> click.Command:
    @cli.command("migrate", short_help="Migrate a STAC object to the latest version")
    @click.argument("href")
    @click.option(
        "-s",
        "--save",
        is_flag=True,
        help="Save migrated STAC object in original location.",
    )
    @click.option(
        "-r",
        "--recursive",
        is_flag=True,
        help="Recurse through all child objects and migrate them as well.",
    )
    @click.option(
        "--show-diff/--hide-diff",
        default=True,
        help=(
            "Whether to dump diff between original and migrated object to stdout. "
            "Defaults to --show-diff. "
        ),
    )
    def migrate_command(
        href: str, save: bool, recursive: bool, show_diff: bool
    ) -> None:
        _migrate(href, save=save, recursive=recursive, show_diff=show_diff)

    return migrate_command
