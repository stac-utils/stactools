import pytest
from pystac import Item
from rasterio.crs import CRS
from shapely.geometry import shape
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon, orient
from stactools.core import use_fsspec
from stactools.core.utils.raster_footprint import (
    data_footprint,
    densify_by_distance,
    densify_by_factor,
    densify_reproject_simplify,
    update_geometry_from_asset_footprint,
)

from tests import test_data


def test_non_existent_asset() -> None:
    use_fsspec()

    item = Item.from_file(
        test_data.get_path(
            "data-files/raster_footprint/MCD43A4.A2001055.h25v06.006.2016113010159.json"
        )
    )

    with pytest.warns(DeprecationWarning):
        assert not (
            update_geometry_from_asset_footprint(
                item,
                asset_names=["B01_doesnt_exist"],
            )
        )


def test_modis() -> None:
    use_fsspec()

    item = Item.from_file(
        test_data.get_path(
            "data-files/raster_footprint/MCD43A4.A2001055.h25v06.006.2016113010159.json"
        )
    )

    with pytest.warns(DeprecationWarning):
        update_geometry_from_asset_footprint(
            item, asset_names=["B01"], densification_factor=10
        )

    geometry = {
        "type": "Polygon",
        "coordinates": (
            (
                [74.4924441, 20.0],
                [75.5566218, 20.0],
                [76.6207996, 20.0],
                [77.6849774, 20.0],
                [78.7491552, 20.0],
                [79.8133329, 20.0],
                [80.8775107, 20.0],
                [81.9416885, 20.0],
                [83.0058662, 20.0],
                [84.070044, 20.0],
                [85.1342218, 20.0],
                [85.6911211, 20.9991667],
                [86.2817654, 21.9983333],
                [86.9072206, 22.9975],
                [87.5686342, 23.9966667],
                [88.2672405, 24.9958333],
                [89.0043673, 25.995],
                [89.781442, 26.9941667],
                [90.5999995, 27.9933333],
                [91.4616898, 28.9925],
                [92.3682877, 29.9916667],
                [92.3657888, 29.9920833],
                [92.36329, 29.9925],
                [92.3607911, 29.9929167],
                [92.3582923, 29.9933333],
                [92.3557934, 29.99375],
                [92.3532945, 29.9941667],
                [92.3507955, 29.9945833],
                [92.3482966, 29.995],
                [92.3457976, 29.9954167],
                [92.3432987, 29.9958333],
                [92.3340642, 29.99625],
                [92.3248296, 29.9966667],
                [92.315595, 29.9970833],
                [92.3063603, 29.9975],
                [92.2971255, 29.9979167],
                [92.2878906, 29.9983333],
                [92.2786557, 29.99875],
                [92.2694207, 29.9991667],
                [92.2601856, 29.9995833],
                [92.2509505, 30.0],
                [91.1097215, 30.0],
                [89.9684924, 30.0],
                [88.8272634, 30.0],
                [87.6860344, 30.0],
                [86.5448053, 30.0],
                [85.4035763, 30.0],
                [84.2623473, 30.0],
                [83.1211182, 30.0],
                [81.9798892, 30.0],
                [80.8386602, 30.0],
                [80.8373585, 29.9995833],
                [80.8360569, 29.9991667],
                [80.8347553, 29.99875],
                [80.8334537, 29.9983333],
                [80.8321521, 29.9979167],
                [80.8308505, 29.9975],
                [80.8295489, 29.9970833],
                [80.8282474, 29.9966667],
                [80.8269459, 29.99625],
                [80.8256443, 29.9958333],
                [80.0318814, 28.99625],
                [79.2774513, 27.9966667],
                [78.560799, 26.9970833],
                [77.8804785, 25.9975],
                [77.2351448, 24.9979167],
                [76.6235472, 23.9983333],
                [76.0445222, 22.99875],
                [75.4969883, 21.9991667],
                [74.9799402, 20.9995833],
                [74.4924441, 20.0],
            ),
        ),
    }
    assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
    assert shape(geometry) == shape(item.geometry)


def test_sentinel2_sliver() -> None:
    use_fsspec()

    item = Item.from_file(
        test_data.get_path(
            "data-files/raster_footprint/S2A_OPER_MSI_L2A_TL_ATOS_20220620T162319_A036527_T32TLS_N04.00.json"  # noqa
        )
    )

    with pytest.warns(DeprecationWarning):
        update_geometry_from_asset_footprint(
            item, asset_names=["R60m_B01"], simplify_tolerance=0.005, no_data=0
        )

    geometry = {
        "type": "Polygon",
        "coordinates": (
            (
                [7.7721445, 46.947125],
                [7.5780704, 46.3833131],
                [7.5325995, 46.2747391],
                [7.42803, 45.9547386],
                [7.8359555, 45.9596225],
                [7.8147104, 46.9475737],
                [7.7721445, 46.947125],
            ),
        ),
    }
    assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
    assert shape(geometry) == shape(item.geometry)


def test_sentinel2_full() -> None:
    use_fsspec()

    item = Item.from_file(
        test_data.get_path(
            "data-files/raster_footprint/S2B_OPER_MSI_L2A_TL_2BPS_20220618T135630_A027590_T32TLS_N04.00.json"  # noqa
        )
    )

    with pytest.warns(DeprecationWarning):
        update_geometry_from_asset_footprint(
            item,
            asset_names=["R60m_B01"],
        )

    geometry = {
        "type": "Polygon",
        "coordinates": (
            (
                [6.3729898, 46.923561],
                [6.4200251, 45.9364192],
                [7.8359555, 45.9596225],
                [7.8147104, 46.9475737],
                [6.3729898, 46.923561],
            ),
        ),
    }
    assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
    assert shape(geometry) == shape(item.geometry)


def test_landsat8() -> None:
    use_fsspec()

    item = Item.from_file(
        test_data.get_path(
            "data-files/raster_footprint/LC08_L1TP_198029_20220331_20220406_02_T1_B2.json"
            # noqa
        )
    )

    with pytest.warns(DeprecationWarning):
        update_geometry_from_asset_footprint(
            item, asset_names=["B2"], simplify_tolerance=0.005
        )

    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [1.3754597, 45.6665645],
                [1.3120683, 45.4817529],
                [1.3145461, 45.3986177],
                [1.8893661, 45.4056547],
                [1.885943, 45.579524],
                [1.3754597, 45.6665645],
            ]
        ],
    }
    assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
    assert shape(geometry) == shape(item.geometry)


def test_nan_as_nodata() -> None:
    with pytest.warns(DeprecationWarning):
        polygon = data_footprint(
            test_data.get_path("data-files/raster_footprint/LC08_LST_crop.tif"),  # noqa
            simplify_tolerance=0.01,
        )
    geometry = {
        "type": "Polygon",
        "coordinates": (
            (
                (-94.721661, 42.4207891),
                (-94.7199638, 42.3586741),
                (-94.6649849, 42.359756),
                (-94.6483633, 42.406737),
                (-94.721661, 42.4207891),
            ),
        ),
    }
    assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
    assert shape(geometry) == shape(polygon)


def test_data_footprint_precision() -> None:
    use_fsspec()

    with pytest.warns(DeprecationWarning):
        polygon = data_footprint(
            test_data.get_path(
                "data-files/raster_footprint/S2A_OPER_MSI_L2A_TL_ATOS_20220620T162319_A036527_T32TLS_N04.00_R60m_B01.jp2"  # noqa
            ),
            precision=1,
            simplify_tolerance=0.01,
            no_data=0,
        )
    geometry = {
        "type": "Polygon",
        "coordinates": (
            (
                (7.5, 46.0),
                (7.8, 46.0),
                (7.8, 46.9),
                (7.7, 46.9),
                (7.7, 46.6),
                (7.6, 46.6),
                (7.6, 46.3),
                (7.5, 46.3),
                (7.5, 46.0),
            ),
        ),
    }
    assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
    assert shape(geometry) == shape(polygon)


def test_reproject() -> None:
    data_polygons = [
        Polygon([[0, 0], [10000, 0], [10000, 10000], [0, 10000], [0, 0]]),
        Polygon(
            [
                [50000, 50000],
                [60000, 50000],
                [60000, 60000],
                [50000, 60000],
                [50000, 50000],
            ]
        ),
        Polygon(
            [
                [80000, 80000],
                [90000, 80000],
                [90000, 90000],
                [80000, 90000],
                [80000, 80000],
            ]
        ),
    ]
    polygon = orient(MultiPolygon(data_polygons).convex_hull)

    reprojected_polygon = densify_reproject_simplify(polygon, CRS.from_epsg(32632))

    geometry = {
        "type": "Polygon",
        "coordinates": (
            (
                (4.5112561, 0),
                (4.6008516, 0),
                (5.3176965, 0.7222805),
                (5.3176192, 0.8125655),
                (5.2279342, 0.8124821),
                (4.5112506, 0.0901938),
                (4.5112561, 0),
            ),
        ),
    }
    assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
    expected = shape(geometry)
    assert reprojected_polygon == expected


def test_remove_duplicate_points() -> None:
    redundant_shape = shape(
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [7.8, 46.9],
                    [7.8, 46.0],
                    [7.4, 46.0],
                    [7.4, 46.0],
                    [7.4, 46.0],
                    [7.4, 46.0],
                    [7.5, 46.0],
                    [7.5, 46.0],
                    [7.5, 46.0],
                    [7.5, 46.0],
                    [7.5, 46.0],
                    [7.5, 46.0],
                    [7.5, 46.0],
                    [7.5, 46.1],
                    [7.5, 46.3],
                    [7.6, 46.3],
                    [7.6, 46.6],
                    [7.8, 46.9],
                ]
            ],
        }
    )

    deduplicated_shape = shape(
        {
            "type": "Polygon",
            "coordinates": [
                (
                    (7.8, 46.9),
                    (7.8, 46),
                    (7.4, 46),
                    (7.5, 46),
                    (7.5, 46.1),
                    (7.5, 46.3),
                    (7.6, 46.3),
                    (7.6, 46.6),
                    (7.8, 46.9),
                )
            ],
        }
    )

    assert (
        densify_reproject_simplify(redundant_shape, CRS.from_epsg(4326))
        == deduplicated_shape
    )


def test_multiband_footprint() -> None:
    path = test_data.get_path(
        "data-files/raster_footprint/"
        "AST_L1T_00310012006175412_20150516104359-SWIR-cropped.tif"
    )
    with pytest.warns(DeprecationWarning):
        footprint = data_footprint(path, no_data=0, bands=[], simplify_tolerance=0.005)
    assert footprint

    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [-105.7853028, 40.4749528],
                [-105.808413, 40.3959062],
                [-105.6366831, 40.3969793],
                [-105.6372387, 40.455872],
                [-105.7853028, 40.4749528],
            ]
        ],
    }
    assert Polygon(geometry["coordinates"][0]).exterior.is_ccw is True
    expected = shape(geometry)
    assert shape(footprint) == expected


def test_densify_by_distance() -> None:
    coords = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)]
    assert len(coords) == 5
    densified_coords = densify_by_distance(coords, 3.33)
    for coord in coords:
        assert coord in densified_coords
    assert len(densified_coords) == 17


def test_densify_by_factor() -> None:
    coords = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)]
    assert len(coords) == 5
    densified_coords = densify_by_factor(coords, 2)
    for coord in coords:
        assert coord in densified_coords
    assert len(densified_coords) == 9
