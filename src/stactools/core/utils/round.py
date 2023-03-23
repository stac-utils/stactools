from typing import Any, List, TypeVar

from pystac import Collection, Item

# Roughly 1 centimeter in geodetic coordinates
DEFAULT_PRECISION = 7

S = TypeVar("S", Item, Collection)


def round_coordinates(stac_object: S, precision: int = DEFAULT_PRECISION) -> S:
    """Rounds Item geometry and bbox coordinates or Collection spatial extent
    bbox coordinates to specified precision.

    Args:
        stac_object (S): A pystac Item or Collection.
        precision (int): Number of decimal places for rounding.

    Returns:
        S: The original PySTAC Item or Collection, with rounded coordinates.
    """
    if isinstance(stac_object, Item):
        if stac_object.geometry is not None:
            stac_object.geometry["coordinates"] = recursive_round(
                list(stac_object.geometry["coordinates"]), precision
            )

        if stac_object.bbox is not None:
            stac_object.bbox = recursive_round(list(stac_object.bbox), precision)

    elif isinstance(stac_object, Collection):
        stac_object.extent.spatial.bboxes = recursive_round(
            list(stac_object.extent.spatial.bboxes), precision
        )

    return stac_object


def recursive_round(coordinates: List[Any], precision: int) -> List[Any]:
    """Rounds a list of numbers. The list can contain additional nested lists
    or tuples of numbers.

    Any tuples encountered will be converted to lists.

    Args:
        coordinates (List[Any]): A list of numbers, possibly containing nested
            lists or tuples of numbers.
        precision (int): Number of decimal places to use for rounding.

    Returns:
        List[Any]: a list (possibly nested) of numbers rounded to the given
            precision.
    """
    for idx, value in enumerate(coordinates):
        if isinstance(value, (int, float)):
            coordinates[idx] = round(value, precision)
        else:
            coordinates[idx] = list(value)  # handle any tuples
            coordinates[idx] = recursive_round(coordinates[idx], precision)
    return coordinates
