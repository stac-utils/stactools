from pathlib import Path
from typing import Any, Dict, List

import pytest
from pystac import Asset, MediaType
from pystac.extensions.file import FileExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import RasterExtension

from stactools.core.builder import (
    Builder,
    RasterioBuilder,
    SingleCOGBuilder,
    SingleFileRasterioBuilder,
)


@pytest.fixture
def cog() -> str:
    return str(
        Path(__file__).parents[1]
        / "data-files"
        / "planet-disaster"
        / "hurricane-harvey"
        / "hurricane-harvey-0831"
        / "Houston-East-20170831-103f-100d-0f4f-RGB"
        / "Houston-East-20170831-103f-100d-0f4f-3-band.tif"
    )


@pytest.fixture
def expected_geometry() -> Dict[str, Any]:
    return {
        "coordinates": [
            [
                [-95.053311, 29.561344],
                [-95.053311, 30.15756],
                [-95.737373, 30.15756],
                [-95.737373, 29.561344],
                [-95.053311, 29.561344],
            ]
        ],
        "type": "Polygon",
    }


@pytest.fixture
def expected_bbox() -> List[float]:
    return [-95.737373, 29.561344, -95.053311, 30.15756]


def test_builder() -> None:
    item = Builder().create_item(id="test-id")
    assert item.id == "test-id"
    assert item.geometry is None
    assert item.bbox is None
    item.validate()


def test_file(cog: str) -> None:
    builder = Builder()
    builder.add_asset("an-asset", Asset(href=cog), include_file_extension=True)
    item = builder.create_item(id="test-id")
    asset = item.assets["an-asset"]
    file = FileExtension.ext(asset)
    assert file.size == 197129
    assert (
        file.checksum
        == "1220afd1280ab204c37001a50b31a576c1567b5ab5a8b6c4653a8b9b53b36b3f6056"
    )
    item.validate()


def test_rasterio_builder(
    cog: str, expected_geometry: Dict[str, Any], expected_bbox: List[float]
) -> None:
    asset = Asset(href=cog)
    builder = RasterioBuilder()
    builder.add_asset("asset-key", asset)
    item = builder.create_item(id="test-id")
    assert item.id == "test-id"
    assert item.geometry is None
    assert item.bbox is None
    item.validate()

    builder.add_rasterio_asset("asset-key-2", asset)
    item = builder.create_item(id="test-id")
    assert item.geometry == expected_geometry
    assert item.bbox == expected_bbox
    ProjectionExtension.validate_has_extension(item, False)
    RasterExtension.validate_has_extension(item, False)
    item.validate()


def test_single_file_builder(
    cog: str, expected_geometry: Dict[str, Any], expected_bbox: List[float]
) -> None:
    item = SingleFileRasterioBuilder.from_href(cog).create_item()
    assert item.id == "Houston-East-20170831-103f-100d-0f4f-3-band"
    assert item.geometry == expected_geometry
    assert item.bbox == expected_bbox
    item.validate()


def test_single_cog_builder(cog: str) -> None:
    item = SingleCOGBuilder.from_href(cog).create_item()
    assert item.assets["data"].media_type == MediaType.COG
    item.validate()
