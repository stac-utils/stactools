import json
import shutil
from pathlib import Path

import pystac
import pytest

from tests import test_data


def expected_json(filename):
    path = Path(__file__).resolve().parent / "expected" / filename
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def planet_disaster() -> pystac.Collection:
    return pystac.Collection.from_file(
        test_data.get_path("data-files/planet-disaster/collection.json")
    )


@pytest.fixture(scope="function")
def tmp_planet_disaster(tmp_path: Path) -> pystac.Collection:
    src = test_data.get_path("data-files/planet-disaster")
    dst = tmp_path / "planet-disaster"
    shutil.copytree(src, str(dst))

    return pystac.Collection.from_file(str(dst / "collection.json"))


@pytest.fixture(scope="function")
def tmp_item_path(tmp_path: Path) -> str:
    src = test_data.get_path("data-files/core/simple-item.json")
    dst = tmp_path / "item.json"
    shutil.copyfile(src, dst)
    return str(dst)


@pytest.fixture(scope="function")
def tmp_asset_path(tmp_path: Path) -> str:
    src = test_data.get_path("data-files/core/byte.tif")
    dst = tmp_path / "byte.tif"
    shutil.copyfile(src, dst)
    return str(dst)
