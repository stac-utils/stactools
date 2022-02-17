import sys
from typing import Any, Dict, List, Optional

import click
import pystac
from contextlib import contextmanager
from pystac import Collection, Item, STACObject, STACObjectType, STACValidationError
from pystac.catalog import Catalog
from pystac.validation import RegisteredValidator, STACValidator

from pystac import Catalog, Collection, Item, STACObject, STACValidationError
from stactools.core.utils import href_exists


def create_validate_command(cli: click.Group) -> click.Command:

    @cli.command("validate", short_help="Validate a stac object.")
    @click.argument("href")
    @click.option("--recurse/--no-recurse",
                  default=True,
                  help=("If false, do not validate any children "
                        "(only useful for Catalogs and Collections)"))
    @click.option("--links/--no-links",
                  default=True,
                  help=("If false, do not check any of the objects's links."))
    @click.option(
        "--assets/--no-assets",
        default=True,
        help=("If false, do not check any of the collection's/item's assets."))
    @click.option("--stac-vrt",
                  is_flag=True,
                  default=False,
                  help=("If true, verify that the required fields exist "
                        "for use by the stac-vrt tool. (default: false)"))
    def validate_command(href, recurse, links, assets, stac_vrt):
        """Validates a STAC object.

        Prints any validation errors to stdout.
        """
        object = pystac.read_file(href)

        validators = [None]  # Start with the existing default
        if stac_vrt:
            validators.append(
                RequiredFieldsValidator({
                    STACObjectType.ITEM:
                    ["proj:bbox", "proj:epsg", "proj:shape", "proj:transform"]
                }))

        errors = []
        for validator in validators:
            if isinstance(object, Item):
                errors += root_validate(validator, object, None, False, links,
                                        assets)
            else:
                errors += root_validate(validator, object, object, recurse,
                                        links, assets)

        if not errors:
            click.secho("OK", fg="green", nl=False)
            click.echo(f" STAC object at {href} is valid!")
        else:
            for error in errors:
                click.secho("ERROR", fg="red", nl=False)
                click.echo(f" {error}")
            sys.exit(1)

    return validate_command


def root_validate(validator: Optional[STACValidator], object: STACObject,
                  root: Optional[STACObject], recurse: bool, links: bool,
                  assets: bool) -> List[str]:
    # A None for validator uses the currently registered STACValidator.

    # Swap to a new validator and safely restore it when finished
    @contextmanager
    def modded(validator: STACValidator):
        old_validator = RegisteredValidator.get_validator()
        RegisteredValidator.set_validator(validator)
        try:
            yield
        finally:
            RegisteredValidator.set_validator(old_validator)

    if validator:
        with modded(validator):
            return validate(object, root, recurse, links, assets)
    else:
        return validate(object, root, recurse, links, assets)


def validate(object: STACObject, root: Optional[STACObject], recurse: bool,
             links: bool, assets: bool) -> List[str]:
    errors: List[str] = []

    try:
        object.validate()
    except FileNotFoundError as e:
        errors.append(f"File not found: {e}")
    except STACValidationError as e:
        errors.append(f"{e}\n{e.source or ''}")

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


class RequiredFieldsValidator(STACValidator):

    def __init__(self, required_fields: Dict[STACObjectType, List[str]]):
        self.required_fields = required_fields

    def validate_core(
        self,
        stac_dict: Dict[str, Any],
        stac_object_type: STACObjectType,
        stac_version: str,
        href: Optional[str] = None,
    ) -> None:
        errors = []
        fields = self.required_fields.get(stac_object_type, [])
        for field in fields:
            if field in stac_dict:
                continue
            if stac_object_type is STACObjectType.ITEM:
                if field in stac_dict["properties"]:
                    continue
            errors.append(f"    Required field: {field}")
        if errors:
            msg = f"Validation failed for {stac_object_type}"
            if href is not None:
                msg += f" at {href}"
            if stac_dict.get("id") is not None:
                msg += f" with ID {stac_dict.get('id')}"
            msg += "\n" + "\n".join(errors) + "\n"
            raise pystac.STACValidationError(msg, source=None)

    def validate_extension(
        self,
        stac_dict: Dict[str, Any],
        stac_object_type: STACObjectType,
        stac_version: str,
        extension_id: str,
        href: Optional[str] = None,
    ) -> None:
        return
