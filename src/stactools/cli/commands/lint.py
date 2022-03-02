import click
import sys
from stac_check.lint import Linter  # type: ignore


def create_lint_command(cli: click.Group) -> click.Command:

    @cli.command("lint", short_help="Lint a stac object with stac-check.")
    @click.option("--quiet",
                  is_flag=True,
                  help=("Do not display the Ok no warnings message."))
    @click.argument("href")
    def lint_command(href: str, quiet: bool) -> None:
        """Lint a STAC object via stac-check.

        Prints any warnings to stdout.
        """
        linter = Linter(href)
        linter_results = linter.create_best_practices_dict()
        if len(linter_results.keys()) == 0 and not quiet:
            click.secho("OK", fg="green", nl=False)
            click.echo(f" STAC object at {href} has no warnings!")
        for _, v in linter_results.items():
            click.secho("WARNING", fg="yellow", nl=False)
            for value in v:
                click.echo(f" {value}")
            sys.exit(1)

    return lint_command
