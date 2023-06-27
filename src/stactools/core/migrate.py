import difflib
import json

import pystac
from pystac.stac_io import DefaultStacIO


def migrate_object(
    href: str, save: bool = False, show_diff: bool = True
) -> pystac.STACObject:
    """Migrate a STAC object and all its extensions to the latest version of STAC

    Note:
        Migrating a STAC object will set the keys to be in the standard order.
        This might result in a diff even for a valid and up-to-date STAC object.

    Args:
        href : Path to the STAC object
        save : Whether to save the object back to its original location.
            Defaults to False.
        show_diff : Whether to print the diff between the original and new STAC
            object. Defaults to True.
    Returns:
        STACObject : The migrated object - modified inplace.
    """
    # migration happens implicitly on load
    stac_object = pystac.read_file(href)
    if show_diff:
        input = DefaultStacIO().read_text(href)
        output = json.dumps(stac_object.to_dict(), indent=2)
        for diffs in difflib.unified_diff(
            input.splitlines(), output.splitlines(), fromfile="before", tofile="after"
        ):
            print(diffs)
    if save:
        stac_object.save_object()
    return stac_object
