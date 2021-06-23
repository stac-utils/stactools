import sys

import click
import pystac


def create_validate_command(cli):
    @cli.command("validate", short_help="Validate a stac object.")
    @click.argument("href")
    @click.option("--only",
                  is_flag=True,
                  help=("Only validate this object, do not validate children "
                        "(only useful for Catalogs and Collections)"))
    def validate_command(href, only):
        """Validates a STAC object.

        Prints any validation errors to stdout.
        """
        object = pystac.read_file(href)
        try:
            if isinstance(object, pystac.Item) or only:
                object.validate()
            else:
                object.validate_all()
            print(f"OK! STAC object at {href} is valid!")
        except pystac.STACValidationError as e:
            print(e)
            print(e.source)
            sys.exit(1)

    return validate_command
