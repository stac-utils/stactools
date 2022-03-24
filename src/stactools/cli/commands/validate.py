import json
import sys
from typing import Optional

import click
from stac_validator.validate import StacValidate


def create_validate_command(cli: click.Group) -> click.Command:
    @cli.command("validate", short_help="Validate a stac object.")
    @click.argument("href")
    @click.option(
        "--recursive/--no-recursive",
        help="Recursively validate all STAC objects in this catalog.",
        default=True,
    )
    @click.option(
        "--validate-links/--no-validate-links", help="Validate links.", default=True
    )
    @click.option(
        "--validate-assets/--no-validate-assets", help="Validate assets.", default=True
    )
    @click.option("-v", "--verbose", is_flag=True, help="Enables verbose output.")
    @click.option(
        "--quiet/--no-quiet", help="Do not print output to console.", default=False
    )
    @click.option(
        "--log-file",
        help="Save output to file (local filepath).",
    )
    def validate_command(
        href: str,
        recursive: bool,
        validate_links: bool,
        validate_assets: bool,
        verbose: bool,
        quiet: bool,
        log_file: Optional[str],
    ) -> None:
        """Validates a STAC object.

        This is a thin wrapper around
        [stac-validate](https://github.com/stac-utils/stac-validator). Not all
        command-line options are exposed. If you want more control over
        validation, use `stac-validator` directly.

        If you'd like linting, use `stac lint`.
        """
        validate = StacValidate(
            href,
            recursive=recursive,
            links=validate_links,
            assets=validate_assets,
            verbose=verbose,
            no_output=quiet,
            log=log_file or "",
        )
        is_valid = validate.run()
        if not quiet:
            click.echo(json.dumps(validate.message, indent=4))
        if is_valid:
            sys.exit(0)
        else:
            sys.exit(1)

    return validate_command
