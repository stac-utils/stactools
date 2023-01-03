from pystac import Collection, Item

from stactools.core.utils.round import round_coordinates
from tests import test_data


def test_item_geometry_bbox() -> None:
    item = Item.from_file(
        test_data.get_path(
            "data-files/catalogs/test-case-1/country-1/area-1-1/"
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
        test_data.get_path("data-files/catalogs/test-case-4/dar/42f235/42f235.json")
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
            "data-files/catalogs/test-case-1/country-1/area-1-1/"
            "area-1-1-imagery/area-1-1-imagery.json"
        )
    )
    item.bbox = None
    item.geometry = None
    item = round_coordinates(item, precision=5)
    assert isinstance(item, Item)


def test_collection_bbox() -> None:
    collection = Collection.from_file(
        test_data.get_path(
            "data-files/catalogs/test-case-1/country-1/area-1-1/collection.json"
        )
    )
    collection = round_coordinates(collection, precision=5)
    coords = collection.extent.spatial.bboxes
    for coord in coords:
        for value in coord:
            assert str(value)[::-1].find(".") <= 5
