import json
import os

import pytest
from pystac.extensions.projection import ProjectionExtension
from stactools.core import create

from tests import test_data


@pytest.fixture(scope="module")
def asset_path() -> str:
    return test_data.get_path(
        "data-files/planet-disaster/hurricane-harvey/"
        "hurricane-harvey-0831/20170831_172754_101c/20170831_172754_101c_3b_Visual.tif"
    )


def test_one_datetime(asset_path: str) -> None:
    item = create.item(asset_path)
    assert os.path.splitext(os.path.basename(asset_path))[0] == item.id
    assert item.datetime is not None

    # convert any tuples to lists
    geojson = json.loads(json.dumps(item.geometry))
    assert geojson == {
        "type": "Polygon",
        "coordinates": [
            [
                [-95.780872, 29.517294],
                [-95.783782, 29.623358],
                [-96.041791, 29.617689],
                [-96.038613, 29.511649],
                [-95.780872, 29.517294],
            ]
        ],
    }
    assert item.bbox == [-96.041791, 29.511649, -95.780872, 29.623358]
    assert item.common_metadata.start_datetime is None
    assert item.common_metadata.end_datetime is None

    projection = ProjectionExtension.ext(item)
    assert projection.epsg == 32615
    assert projection.wkt2 is None
    assert projection.projjson is None
    assert projection.transform == [
        97.69921875,
        0.0,
        205437.0,
        0.0,
        -45.9609375,
        3280290.0,
    ]

    assert projection.shape == (256, 256)

    data = item.assets["data"]
    assert data.href == asset_path
    assert data.title is None
    assert data.description is None
    assert data.roles == ["data"]
    assert data.media_type is None
    item.validate()


def test_read_href_modifer(asset_path: str) -> None:
    did_it = False

    def do_it(href: str) -> str:
        nonlocal did_it
        did_it = True
        return href

    item = create.item(asset_path, read_href_modifier=do_it)
    assert did_it
    assert item.id == "20170831_172754_101c_3b_Visual"
