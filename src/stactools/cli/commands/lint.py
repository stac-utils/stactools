import sys
from typing import Optional

import click
from stac_check.lint import Linter  # type: ignore


def create_lint_command(cli: click.Group) -> click.Command:
    @cli.command("lint", short_help="Lint a stac object with stac-check.")
    @click.option(
        "--quiet",
        is_flag=True,
        help=(
            "Do not print anything to standard output, "
            "simply set the process exit code to 1 on error."
        ),
    )
    @click.option(
        "--config-file",
        help="Path to a configuration file to use instead of the default configuration",
    )
    @click.argument("href")
    def lint_command(href: str, quiet: bool, config_file: Optional[str]) -> None:
        """Lint a STAC object via stac-check.

        Prints any warnings to stdout.

        stac-check: https://github.com/stac-utils/stac-check
        """
        linter = Linter(href, config_file=config_file)
        if not config_file:
            # While this is currently recommended in the STAC best practices,
            # this conflicts with the best practices layouts, so we silence the
            # warning. See https://github.com/radiantearth/stac-spec/pull/1173
            # for more information.
            linter.config["linting"]["links_self"] = False
        linter_results = linter.create_best_practices_dict()
        if len(linter_results.keys()) == 0:
            if not quiet:
                click.secho("OK", fg="green", nl=False)
                click.echo(f" STAC object at {href} has no warnings!")
        else:
            if not quiet:
                for _, v in linter_results.items():
                    click.secho("WARNING", fg="yellow", nl=False)
                    for value in v:
                        click.echo(f" {value}")
            sys.exit(1)

    return lint_command
