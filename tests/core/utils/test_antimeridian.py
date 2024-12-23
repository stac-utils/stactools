import datetime

import pytest
import shapely.geometry
from pystac import Item
from shapely.geometry import MultiPolygon, Polygon

from stactools.core.utils import antimeridian


def test_antimeridian_normalize() -> None:
    canonical = Polygon(((170, 40), (170, 50), (-170, 50), (-170, 40), (170, 40)))
    with pytest.warns(DeprecationWarning):
        normalized = antimeridian.normalize(canonical)
    assert normalized
    assert normalized.exterior.is_ccw
    expected = shapely.geometry.box(170, 40, 190, 50)
    assert normalized.equals(expected), f"actual={normalized}, expected={expected}"

    canonical_other_way = Polygon(
        ((-170, 40), (170, 40), (170, 50), (-170, 50), (-170, 40)),
    )
    with pytest.warns(DeprecationWarning):
        normalized = antimeridian.normalize(canonical_other_way)
    assert normalized
    assert normalized.exterior.is_ccw
    expected = shapely.geometry.box(-170, 40, -190, 50)
    assert normalized.equals(expected), f"actual={normalized}, expected={expected}"


def test_antimeridian_normalize_westerly() -> None:
    westerly = Polygon(((170, 40), (170, 50), (-140, 50), (-140, 40), (170, 40)))
    with pytest.warns(DeprecationWarning):
        normalized = antimeridian.normalize(westerly)
    assert normalized
    assert normalized.exterior.is_ccw
    expected = shapely.geometry.box(-170, 40, -190, 50)
    expected = shapely.geometry.box(-190, 40, -140, 50)
    assert normalized.equals(expected), f"actual={normalized}, expected={expected}"


def test_antimeridian_normalize_easterly() -> None:
    easterly = Polygon(((-170, 40), (140, 40), (140, 50), (-170, 50), (-170, 40)))
    with pytest.warns(DeprecationWarning):
        normalized = antimeridian.normalize(easterly)
    assert normalized
    assert normalized.exterior.is_ccw
    expected = shapely.geometry.box(-170, 40, -190, 50)
    expected = shapely.geometry.box(140, 40, 190, 50)
    assert normalized.equals(expected), f"actual={normalized}, expected={expected}"


def test_item_fix_antimeridian_normalize() -> None:
    canonical = Polygon(((170, 40), (170, 50), (-170, 50), (-170, 40), (170, 40)))
    item = Item(
        "an-id",
        geometry=shapely.geometry.mapping(canonical),
        bbox=canonical.bounds,
        datetime=datetime.datetime.now(),
        properties={},
    )
    with pytest.warns(DeprecationWarning):
        fix = antimeridian.fix_item(item, antimeridian.Strategy.NORMALIZE)
    expected = shapely.geometry.box(170, 40, 190, 50)
    assert shapely.geometry.shape(fix.geometry).equals(expected)
    assert fix.bbox
    assert list(fix.bbox) == [170.0, 40.0, 190.0, 50.0]


def test_item_fix_antimeridian_multipolygon_ok() -> None:
    split = MultiPolygon(
        (
            shapely.geometry.box(170, 40, 180, 50),
            shapely.geometry.box(-180, 40, -170, 50),
        ),
    )
    item = Item(
        "an-id",
        geometry=shapely.geometry.mapping(split),
        bbox=split.bounds,
        datetime=datetime.datetime.now(),
        properties={},
    )
    antimeridian.fix_item(item, antimeridian.Strategy.SPLIT)
    with pytest.warns(DeprecationWarning):
        antimeridian.fix_item(item, antimeridian.Strategy.NORMALIZE)
