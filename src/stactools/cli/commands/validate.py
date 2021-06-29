import sys
from typing import Optional

import click
import pystac
from pystac import Item, Catalog, STACValidationError, STACObject


def create_validate_command(cli):
    @cli.command("validate", short_help="Validate a stac object.")
    @click.argument("href")
    @click.option("--recurse/--no-recurse",
                  default=True,
                  help=("If false, do not validate any children "
                        "(only useful for Catalogs and Collections"))
    @click.option("--links/--no-links",
                  default=True,
                  help=("If false, do not check any of the item's links."))
    def validate_command(href, recurse, links):
        """Validates a STAC object.

        Prints any validation errors to stdout.
        """
        object = pystac.read_file(href)

        errors = []
        errors += validation_errors(object, recurse)
        if links:
            if isinstance(object, Item):
                errors += link_errors(object, None)
            else:
                errors += link_errors(object, object)

        if not errors:
            click.secho("OK", fg="green", nl=False)
            click.echo(f" STAC object at {href} is valid!")
        else:
            for error in errors:
                click.secho("ERROR", fg="red", nl=False)
                click.echo(f" {error}")
            sys.exit(1)

    return validate_command


def validation_errors(object: STACObject, recurse: bool):
    try:
        if isinstance(object, Item) or not recurse:
            object.validate()
        else:
            object.validate_all()
    except FileNotFoundError as e:
        return [f"File not found: {e}"]
    except STACValidationError as e:
        return [f"{e}\n{e.source}"]
    else:
        return []


def link_errors(object: STACObject, root: Optional[Catalog]):
    errors = []
    for link in object.get_links():
        try:
            link = link.resolve_stac_object(root)
        except FileNotFoundError:
            errors.append(
                f"Missing link in {object.self_href}: \"{link.rel}\" -> {link.href}"
            )
        else:
            if link.rel == "child" or link.rel == "item":
                errors += link_errors(link.target, root)
    return errors
