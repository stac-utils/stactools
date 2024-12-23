import pystac
import pystac.utils
import pytest
from click.testing import CliRunner

from stactools.cli.cli import cli
from tests import test_data


@pytest.fixture(scope="module")
def item_path() -> str:
    return test_data.get_path(
        "data-files/basic/country-1/area-1-1"
        "/area-1-1-imagery/area-1-1-imagery-invalid.json"
    )


def test_add_item(item_path: str, tmp_planet_disaster: pystac.Collection):
    collection = tmp_planet_disaster
    collection_path = collection.get_self_href()
    items = list(collection.get_items(recursive=True))
    assert len(items) == 5

    runner = CliRunner()
    result = runner.invoke(cli, ["add", item_path, collection_path])
    assert result.exit_code == 0

    collection_after = pystac.read_file(collection_path)
    items = list(collection_after.get_items(recursive=True))
    assert len(items) == 6


def test_add_item_to_specific_collection(
    item_path: str, tmp_planet_disaster: pystac.Collection
):
    collection = tmp_planet_disaster
    collection_path = collection.get_self_href()
    items = list(collection.get_items(recursive=True))
    assert len(items) == 5
    item_before = pystac.read_file(item_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "add",
            item_path,
            collection_path,
            "--collection",
            "hurricane-harvey",
        ],
    )
    assert result.exit_code == 0

    collection_after = pystac.read_file(collection_path)
    items_after = collection_after.get_child("hurricane-harvey").get_items()
    assert any(item.id == item_before.id for item in items_after)


def test_add_item_to_missing_collection(
    item_path: str, tmp_planet_disaster: pystac.Collection
):
    collection = tmp_planet_disaster
    collection_path = collection.get_self_href()
    items = list(collection.get_items(recursive=True))
    assert len(items) == 5

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "add",
            item_path,
            collection_path,
            "--collection",
            "WRONG",
        ],
    )
    assert result.exit_code == 2
    assert " A collection with ID WRONG does not exist" in result.output
