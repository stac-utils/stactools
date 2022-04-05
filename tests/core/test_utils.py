import datetime
import os.path
import unittest
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import pytest
import rasterio
import shapely.geometry
from pystac import Item
from shapely.geometry import MultiPolygon, Polygon

from stactools.core.utils import antimeridian
from stactools.core.utils.convert import cogify
from tests import test_data


class CogifyTest(unittest.TestCase):
    @contextmanager
    def cogify(self, **kwargs):
        infile = test_data.get_path("data-files/core/byte.tif")
        with TemporaryDirectory() as directory:
            outfile = os.path.join(directory, "byte.tif")
            cogify(infile, outfile, **kwargs)
            yield outfile

    def test_default(self):
        with self.cogify() as outfile:
            self.assertTrue(os.path.exists(outfile))
            with rasterio.open(outfile) as dataset:
                self.assertEqual(
                    dataset.compression, rasterio.enums.Compression.deflate
                )

    def test_profile(self):
        with self.cogify(profile={"compress": "lzw"}) as outfile:
            self.assertTrue(os.path.exists(outfile))
            with rasterio.open(outfile) as dataset:
                self.assertEqual(dataset.compression, rasterio.enums.Compression.lzw)


def test_antimeridian_split() -> None:
    # From https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.9
    canonical = Polygon(((170, 40), (170, 50), (-170, 50), (-170, 40), (170, 40)))
    split = antimeridian.split(canonical)
    assert split
    expected = MultiPolygon(
        (
            shapely.geometry.box(170, 40, 180, 50),
            shapely.geometry.box(-180, 40, -170, 50),
        )
    )
    for actual, expected in zip(split.geoms, expected.geoms):
        assert actual.equals(expected)

    doesnt_cross = Polygon(((170, 40), (170, 50), (180, 50), (180, 40), (170, 40)))
    split = antimeridian.split(doesnt_cross)
    assert split is None

    canonical_other_way = Polygon(
        ((-170, 40), (170, 40), (170, 50), (-170, 50), (-170, 40))
    )
    split = antimeridian.split(canonical_other_way)
    assert split
    expected = MultiPolygon(
        (
            shapely.geometry.box(-180, 40, -170, 50),
            shapely.geometry.box(170, 40, 180, 50),
        )
    )
    for actual, expected in zip(split.geoms, expected.geoms):
        assert actual.equals(expected), f"actual={actual}, expected={expected}"


def test_antimeridian_split_complicated() -> None:
    complicated = Polygon(
        ((170, 40), (170, 50), (-170, 50), (170, 45), (-170, 40), (170, 40))
    )
    split = antimeridian.split(complicated)
    assert split
    expected = MultiPolygon(
        (
            Polygon(((170, 40), (170, 45), (180, 42.5), (180, 40), (170, 40))),
            Polygon(((170, 45), (170, 50), (180, 50), (180, 47.5), (170, 45))),
            Polygon(((-180, 50), (-170, 50), (-180, 47.5), (-180, 50))),
            Polygon(((-180, 42.5), (-170, 40), (-180, 40), (-180, 42.5))),
        )
    )
    for actual, expected in zip(split.geoms, expected.geoms):
        assert actual.equals(expected), f"actual={actual}, expected={expected}"


def test_antimeridian_normalize() -> None:
    canonical = Polygon(((170, 40), (170, 50), (-170, 50), (-170, 40), (170, 40)))
    normalized = antimeridian.normalize(canonical)
    assert normalized
    expected = shapely.geometry.box(170, 40, 190, 50)
    assert normalized.equals(expected), f"actual={normalized}, expected={expected}"

    canonical_other_way = Polygon(
        ((-170, 40), (170, 40), (170, 50), (-170, 50), (-170, 40))
    )
    normalized = antimeridian.normalize(canonical_other_way)
    assert normalized
    expected = shapely.geometry.box(-170, 40, -190, 50)
    assert normalized.equals(expected), f"actual={normalized}, expected={expected}"


def test_antimeridian_normalize_westerly() -> None:
    westerly = Polygon(((170, 40), (170, 50), (-140, 50), (-140, 40), (170, 40)))
    normalized = antimeridian.normalize(westerly)
    assert normalized
    expected = shapely.geometry.box(-190, 40, -140, 50)
    assert normalized.equals(expected), f"actual={normalized}, expected={expected}"


def test_antimeridian_normalize_easterly() -> None:
    easterly = Polygon(((-170, 40), (140, 40), (140, 50), (-170, 50), (-170, 40)))
    normalized = antimeridian.normalize(easterly)
    assert normalized
    expected = shapely.geometry.box(140, 40, 190, 50)
    assert normalized.equals(expected), f"actual={normalized}, expected={expected}"


def test_item_fix_antimeridian_split() -> None:
    canonical = Polygon(((170, 40), (170, 50), (-170, 50), (-170, 40), (170, 40)))
    item = Item(
        "an-id",
        geometry=shapely.geometry.mapping(canonical),
        bbox=canonical.bounds,
        datetime=datetime.datetime.now(),
        properties={},
    )
    antimeridian.fix_item(item, antimeridian.Strategy.SPLIT)
    expected = MultiPolygon(
        (
            shapely.geometry.box(170, 40, 180, 50),
            shapely.geometry.box(-180, 40, -170, 50),
        )
    )
    for actual, expected in zip(
        shapely.geometry.shape(item.geometry).geoms, expected.geoms
    ):
        assert actual.equals(expected)
    assert item.bbox == [170, 40, -170, 50]


def test_item_fix_antimeridian_normalize() -> None:
    canonical = Polygon(((170, 40), (170, 50), (-170, 50), (-170, 40), (170, 40)))
    item = Item(
        "an-id",
        geometry=shapely.geometry.mapping(canonical),
        bbox=canonical.bounds,
        datetime=datetime.datetime.now(),
        properties={},
    )
    antimeridian.fix_item(item, antimeridian.Strategy.NORMALIZE)
    expected = shapely.geometry.box(170, 40, 190, 50)
    assert shapely.geometry.shape(item.geometry).equals(expected)
    assert item.bbox
    assert list(item.bbox) == [170.0, 40.0, 190.0, 50.0]


def test_item_fix_antimeridian_multipolygon_failure() -> None:
    split = MultiPolygon(
        (
            shapely.geometry.box(170, 40, 180, 50),
            shapely.geometry.box(-180, 40, -170, 50),
        )
    )
    item = Item(
        "an-id",
        geometry=shapely.geometry.mapping(split),
        bbox=split.bounds,
        datetime=datetime.datetime.now(),
        properties={},
    )
    with pytest.raises(ValueError):
        antimeridian.fix_item(item, antimeridian.Strategy.SPLIT)
    with pytest.raises(ValueError):
        antimeridian.fix_item(item, antimeridian.Strategy.NORMALIZE)
