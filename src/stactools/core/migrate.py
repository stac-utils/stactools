import difflib
import json
from itertools import chain

import pystac
from pystac.stac_io import DefaultStacIO


def _print_diff(stac_object: pystac.STACObject) -> None:
    href = stac_object.get_self_href()
    if href is None:
        raise ValueError(f"Could not determine diff for {stac_object}, missing href")
    input = DefaultStacIO().read_text(href)
    output = json.dumps(stac_object.to_dict(), indent=2)
    for diffs in difflib.unified_diff(
        input.splitlines(), output.splitlines(), fromfile=f"a{href}", tofile=f"b{href}"
    ):
        print(diffs)


def migrate_object(
    stac_object: pystac.STACObject,
    save: bool = False,
    recursive: bool = False,
    show_diff: bool = True,
) -> pystac.STACObject:
    """Migrate a STAC object and all its extensions to the latest version of STAC

    Note:
        Migrating a STAC object will set the keys to be in the standard order.
        This might result in a diff even for a valid and up-to-date STAC object.

    Args:
        stac_object : STAC object to migrate
        save : Whether to save the object back to its original location.
            Defaults to False.
        recursive : Whether to recurse through all the child object and migrate
            them as well. Defaults to False.
        show_diff : Whether to print the diff between the original and new STAC
            object. Defaults to True.
    Returns:
        STACObject : The migrated object - modified inplace.
    """
    # migration happens implicitly on load
    if show_diff:
        _print_diff(stac_object)

    if recursive:
        if not isinstance(stac_object, (pystac.Catalog, pystac.Collection)):
            raise KeyError(
                "'recursive' is only a valid option for "
                "pystac.Catalogs and pystac.Collections"
            )
        stac_object.fully_resolve()
        if show_diff:
            for _, children, items in stac_object.walk():
                for obj in chain(children, items):
                    _print_diff(obj)
        if save:
            stac_object.save()
    else:
        if save:
            stac_object.save_object()

    return stac_object
