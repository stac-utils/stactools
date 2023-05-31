import datetime

import pytest
import shapely.geometry
from pystac import Item
from shapely.geometry import MultiPolygon, Polygon
from stactools.core.utils import antimeridian


def test_antimeridian_split() -> None:
    # From https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.9
    canonical = Polygon(((170, 40), (-170, 40), (-170, 50), (170, 50), (170, 40)))
    with pytest.warns(DeprecationWarning):
        split = antimeridian.split(canonical)
    assert split
    expected = MultiPolygon(
        (
            shapely.geometry.box(170, 40, 180, 50),
            shapely.geometry.box(-180, 40, -170, 50),
        ),
    )
    for actual, expected in zip(split.geoms, expected.geoms):
        assert actual.exterior.is_ccw
        assert actual.equals(expected)

    doesnt_cross = Polygon(((170, 40), (170, 50), (180, 50), (180, 40), (170, 40)))
    with pytest.warns(DeprecationWarning):
        split = antimeridian.split(doesnt_cross)
    assert split is None

    canonical_other_way = Polygon(
        ((-170, 40), (-170, 50), (170, 50), (170, 40), (-170, 40)),
    )
    with pytest.warns(DeprecationWarning):
        split = antimeridian.split(canonical_other_way)
    assert split
    expected = MultiPolygon(
        (
            shapely.geometry.box(-180, 40, -170, 50),
            shapely.geometry.box(170, 40, 180, 50),
        ),
    )
    for actual, expected in zip(split.geoms, expected.geoms):
        assert actual.exterior.is_ccw
        assert actual.equals(expected), f"actual={actual}, expected={expected}"


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


def test_item_fix_antimeridian_split() -> None:
    canonical = Polygon(((170, 40), (-170, 40), (-170, 50), (170, 50), (170, 40)))
    item = Item(
        "an-id",
        geometry=shapely.geometry.mapping(canonical),
        bbox=canonical.bounds,
        datetime=datetime.datetime.now(),
        properties={},
    )
    fix = antimeridian.fix_item(item, antimeridian.Strategy.SPLIT)
    expected = MultiPolygon(
        (
            shapely.geometry.box(170, 40, 180, 50),
            shapely.geometry.box(-180, 40, -170, 50),
        ),
    )
    for actual, expected in zip(
        shapely.geometry.shape(fix.geometry).geoms,
        expected.geoms,
    ):
        assert actual.equals(expected)
    assert fix.bbox == [170.0, 40.0, -170.0, 50.0]

    # https://github.com/stac-utils/stactools/issues/431
    item.geometry = {
        "type": "MultiPolygon",
        "coordinates": [
            [
                [
                    [180.0, 71.05915991175688],
                    [179.9010750820252, 71.06541838862726],
                    [179.33609176796372, 71.09933099986762],
                    [178.94212273834066, 71.12173675373532],
                    [178.8438129745677, 70.9444458447684],
                    [178.752152818998, 70.76646311814699],
                    [178.65805412647518, 70.58865453189631],
                    [178.56519747139944, 70.41081414405018],
                    [178.47354940789182, 70.23294268101853],
                    [178.3830776723032, 70.0550408551604],
                    [178.29375108586135, 69.87710927076108],
                    [178.20553958576738, 69.69914858383564],
                    [178.11841414688843, 69.52115944285417],
                    [177.94089921353645, 69.16547224310027],
                    [177.84841186280488, 68.98789251198602],
                    [177.6811017579393, 68.63180788289334],
                    [177.59856429364814, 68.45374564350413],
                    [177.5170097254968, 68.27565414719149],
                    [177.35557827100007, 67.91945640451053],
                    [177.27786157853095, 67.74121946580148],
                    [177.2008812187222, 67.5629645683486],
                    [177.04801561874308, 67.20647273987551],
                    [176.999842641033, 67.08652173541694],
                    [177.33004216473563, 67.06599963683973],
                    [177.80402381607067, 67.0350911283458],
                    [178.2797509869322, 67.00256994873874],
                    [178.75469524409255, 66.96859439018418],
                    [179.22826647862672, 66.9332058638613],
                    [179.69748316523564, 66.89664359586376],
                    [180.0, 66.87210508518304],
                    [180.0, 71.05915991175688],
                ]
            ],
            [
                [
                    [-180.0, 71.05915991175688],
                    [-180.0, 66.87210508518304],
                    [-179.8356900497663, 66.85877716089777],
                    [-179.3711345161936, 66.81960857957779],
                    [-178.90872065703624, 66.77913696435182],
                    [-178.44665752494657, 66.73720767705268],
                    [-177.98865515860075, 66.69416388262516],
                    [-177.52780114205189, 66.6493554890298],
                    [-177.07275963647132, 66.6036210941224],
                    [-176.60787845770125, 66.55536115330877],
                    [-176.1601824748328, 66.50739485114256],
                    [-175.70001915807038, 66.4565657047866],
                    [-175.2469931583778, 66.40499213010705],
                    [-174.7964900612594, 66.35218457280217],
                    [-174.34347993447946, 66.29754039236374],
                    [-173.93806864778026, 66.24724531349037],
                    [-173.84461372118676, 66.36429279141416],
                    [-173.71659543892704, 66.53996608675018],
                    [-173.56903550480715, 66.7133044234658],
                    [-173.42527581962764, 66.88723670581788],
                    [-173.13377948252224, 67.23496576919374],
                    [-172.9861602177385, 67.40878187666635],
                    [-172.83662520799953, 67.58248608985471],
                    [-172.68512898875264, 67.75607579888592],
                    [-172.53162554562746, 67.92954828162647],
                    [-172.3760685337871, 68.10290084143905],
                    [-172.2184100683418, 68.27613086321372],
                    [-172.05860098199193, 68.44923546830157],
                    [-171.89659058995878, 68.6222117159503],
                    [-171.73232652538707, 68.79505671303144],
                    [-171.5657549702618, 68.96776730324396],
                    [-171.39682036750511, 69.14034030642564],
                    [-171.2254655001628, 69.31277236817284],
                    [-171.0516311905371, 69.48506019171748],
                    [-170.87525658150514, 69.65720018398522],
                    [-170.6962788340423, 69.82918868566634],
                    [-170.51463300157428, 70.00102201028209],
                    [-170.33062092998924, 70.17235288521945],
                    [-170.8013714414895, 70.22969914468295],
                    [-171.32505679115005, 70.2915919758267],
                    [-171.85186730974112, 70.35195515326475],
                    [-172.3817527878377, 70.41077446610994],
                    [-172.9146602469648, 70.46803605371709],
                    [-173.45053416371871, 70.52372627412625],
                    [-173.98931653005684, 70.5778316447626],
                    [-174.53094682771086, 70.6303388535604],
                    [-175.07536190589843, 70.68123489897708],
                    [-175.62249600000058, 70.73050710549359],
                    [-176.17228091814727, 70.77814294613066],
                    [-176.72464582082006, 70.82413036939441],
                    [-177.2795175859301, 70.86845740126327],
                    [-177.83682058594974, 70.91111247989673],
                    [-178.39647668879172, 70.95208453426882],
                    [-178.96676234549457, 70.99192936610521],
                    [-179.53562414647374, 71.02978121124382],
                    [-180.0, 71.05915991175688],
                ]
            ],
        ],
    }
    fix = antimeridian.fix_item(item, antimeridian.Strategy.SPLIT)
    assert fix.bbox == [
        176.999842641033,
        66.24724531349037,
        -170.33062092998924,
        71.12173675373532,
    ]


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


def test_antimeridian_multipolygon() -> None:
    multi_polygon = MultiPolygon(
        [
            Polygon(((170, 40), (-170, 40), (-170, 42), (170, 42), (170, 40))),
            Polygon(((170, 48), (-170, 48), (-170, 50), (170, 50), (170, 48))),
        ],
    )
    with pytest.warns(DeprecationWarning):
        split = antimeridian.split_multipolygon(multi_polygon)
    assert split
    expected = MultiPolygon(
        (
            shapely.geometry.box(170, 40, 180, 42),
            shapely.geometry.box(-180, 40, -170, 42),
            shapely.geometry.box(170, 48, 180, 50),
            shapely.geometry.box(-180, 48, -170, 50),
        ),
    )
    for actual, expected in zip(split.geoms, expected.geoms):
        assert actual.exterior.is_ccw
        assert actual.equals(expected), f"actual={actual}, expected={expected}"

    with pytest.warns(DeprecationWarning):
        normalized = antimeridian.normalize_multipolygon(multi_polygon)
    assert normalized
    expected = MultiPolygon(
        (
            Polygon(((170, 40), (170, 42), (190, 42), (190, 40), (170, 40))),
            Polygon(((170, 48), (170, 50), (190, 50), (190, 48), (170, 48))),
        ),
    )
    for actual, expected in zip(normalized.geoms, expected.geoms):
        assert actual.exterior.is_ccw
        assert actual.equals(expected), f"actual={actual}, expected={expected}"
