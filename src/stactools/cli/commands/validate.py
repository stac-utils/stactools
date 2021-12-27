import sys
from typing import Optional, List

import click
import pystac

from pystac import Catalog, Collection, Item, STACObject, STACValidationError
from stactools.core.utils import href_exists


def create_validate_command(cli: click.Group) -> click.Command:

    @cli.command("validate", short_help="Validate a stac object.")
    @click.argument("href")
    @click.option("--recurse/--no-recurse",
                  default=True,
                  help=("If false, do not validate any children "
                        "(only useful for Catalogs and Collections"))
    @click.option("--links/--no-links",
                  default=True,
                  help=("If false, do not check any of the objects's links."))
    @click.option(
        "--assets/--no-assets",
        default=True,
        help=("If false, do not check any of the collection's/item's assets."))
    def validate_command(href: str, recurse: bool, links: bool,
                         assets: bool) -> None:
        """Validates a STAC object.

        Prints any validation errors to stdout.
        """
        object = pystac.read_file(href)

        if isinstance(object, Item):
            errors = validate(object, None, False, links, assets)
        else:
            errors = validate(object, object, recurse, links, assets)

        if not errors:
            click.secho("OK", fg="green", nl=False)
            click.echo(f" STAC object at {href} is valid!")
        else:
            for error in errors:
                click.secho("ERROR", fg="red", nl=False)
                click.echo(f" {error}")
            sys.exit(1)

    return validate_command


def validate(object: STACObject, root: Optional[STACObject], recurse: bool,
             links: bool, assets: bool) -> List[str]:
    errors: List[str] = []

    try:
        object.validate()
    except FileNotFoundError as e:
        errors.append(f"File not found: {e}")
    except STACValidationError as e:
        errors.append(f"{e}\n{e.source}")

    if links:
        for link in object.get_links():
            href = link.get_absolute_href()
            assert href
            if not href_exists(href):
                errors.append(
                    f"Missing link in {object.self_href}: \"{link.rel}\" -> {link.href}"
                )

    if assets and (isinstance(object, Item) or isinstance(object, Collection)):
        for name, asset in object.get_assets().items():
            href = asset.get_absolute_href()
            assert href
            if not href_exists(href):
                errors.append(
                    f"Asset '{name}' does not exist: {asset.get_absolute_href()}"
                )

    if recurse:
        assert isinstance(object, Catalog) or isinstance(object, Collection)
        for child in object.get_children():
            errors.extend(validate(child, root, recurse, links, assets))
        for item in object.get_items():
            errors.extend(validate(item, root, False, links, assets))

    return errors
