import sys

import click
import pystac
from pystac import Item, Catalog, STACValidationError, STACObject


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
        errors = []
        errors += validation_errors(object, only)
        errors += link_errors(object, object)
        if not (isinstance(object, Item) or only):
            errors += child_errors(object, object)
        if not errors:
            click.secho("OK", fg="green", nl=False)
            click.echo(f" STAC object at {href} is valid!")
        else:
            for error in errors:
                click.secho("ERROR", fg="red", nl=False)
                click.echo(f" {error}")
            sys.exit(1)

    return validate_command


def validation_errors(object: STACObject, only: bool):
    try:
        if isinstance(object, Item) or only:
            object.validate()
        else:
            object.validate_all()
    except FileNotFoundError as e:
        return [f"File not found: {e}"]
    except STACValidationError as e:
        return [f"{e}\n{e.source}"]
    else:
        return []


def child_errors(root: Catalog, object: Catalog):
    errors = []
    for link in object.get_child_links():
        try:
            link = link.resolve_stac_object(root)
        except FileNotFoundError:
            errors.append(
                f"{object.self_href} has a missing child link: {link.href}")
        else:
            errors += child_errors(root, link.target)
            errors += link_errors(root, link.target)
    return errors


def link_errors(root: Catalog, object: Catalog):
    errors = []
    for link in object.get_links():
        try:
            link.resolve_stac_object(root)
        except FileNotFoundError:
            errors.append(
                f"{object.self_href} has a missing \"{link.rel}\" link: {link.href}"
            )
    return errors
