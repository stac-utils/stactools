from typing import Any, Iterable, Iterator

from pystac import Collection, Item

from stactools.core.utils.round import recursive_round, round_coordinates
from tests import test_data


def test_item_geometry_bbox() -> None:
    item = Item.from_file(
        test_data.get_path(
            "data-files/basic/country-1/area-1-1/"
            "area-1-1-imagery/area-1-1-imagery.json"
        )
    )
    item = round_coordinates(item, precision=5)

    polys = item.geometry["coordinates"]
    for poly in polys:
        for coord in poly:
            for value in coord:
                assert str(value)[::-1].find(".") <= 5

    bbox = item.bbox
    for value in bbox:
        assert str(value)[::-1].find(".") <= 5


def test_item_multipolygon_geometry() -> None:
    item = Item.from_file(
        test_data.get_path("data-files/training/dar/42f235/42f235.json")
    )
    item = round_coordinates(item, precision=5)

    polys = item.geometry["coordinates"]
    for poly in polys:
        for subpoly in poly:
            for coord in subpoly:
                for value in coord:
                    assert str(value)[::-1].find(".") <= 5

    bbox = item.bbox
    for value in bbox:
        assert str(value)[::-1].find(".") <= 5


def test_item_no_geometry_or_bbox() -> None:
    item = Item.from_file(
        test_data.get_path(
            "data-files/basic/country-1/area-1-1/"
            "area-1-1-imagery/area-1-1-imagery.json"
        )
    )
    item.bbox = None
    item.geometry = None
    item = round_coordinates(item, precision=5)
    assert isinstance(item, Item)


def test_collection_bbox() -> None:
    collection = Collection.from_file(
        test_data.get_path("data-files/basic/country-1/area-1-1/collection.json")
    )
    collection = round_coordinates(collection, precision=5)
    coords = collection.extent.spatial.bboxes
    for coord in coords:
        for value in coord:
            assert str(value)[::-1].find(".") <= 5


def test_recursive_round() -> None:
    def flatten(nested: Iterable) -> Iterator[Any]:
        for value in nested:
            if isinstance(value, Iterable):
                for nest in flatten(value):
                    yield nest
            else:
                yield value

    vanilla = [0.123456, 1.12345678]
    rounded = recursive_round(vanilla, precision=4)
    for coord in rounded:
        assert str(coord)[::-1].find(".") == 4

    nested_lists = [
        [[0.123456, 2.1234567], [1.12345678, 2.12345]],
        [[0.123456, 1.12345678]],
    ]
    rounded = recursive_round(nested_lists, precision=3)
    for coord in flatten(rounded):
        assert str(coord)[::-1].find(".") == 3

    nested_tuples = [
        ((0.123456, 2.1234567), (1.12345678, 2.12345)),
        ((0.123456, 1.12345678)),
    ]
    rounded = recursive_round(nested_tuples, precision=5)
    for coord in flatten(rounded):
        assert str(coord)[::-1].find(".") == 5
