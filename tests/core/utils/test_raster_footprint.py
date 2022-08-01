from pystac import Item
from rasterio.crs import CRS
from shapely.geometry import shape
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon

from stactools.core import use_fsspec
from stactools.core.utils.raster_footprint import (
    data_footprint,
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

    update_geometry_from_asset_footprint(
        item, asset_names=["B01"], densification_factor=10
    )

    geometry = {
        "type": "Polygon",
        "coordinates": (
            (
                (74.492, 20.0),
                (74.98, 21.0),
                (75.497, 21.999),
                (76.045, 22.999),
                (76.624, 23.998),
                (77.235, 24.998),
                (77.88, 25.997),
                (78.561, 26.997),
                (79.277, 27.997),
                (80.032, 28.996),
                (80.826, 29.996),
                (80.827, 29.996),
                (80.828, 29.997),
                (80.83, 29.997),
                (80.831, 29.997),
                (80.832, 29.998),
                (80.833, 29.998),
                (80.835, 29.999),
                (80.836, 29.999),
                (80.837, 30.0),
                (80.839, 30.0),
                (81.98, 30.0),
                (83.121, 30.0),
                (84.262, 30.0),
                (85.404, 30.0),
                (86.545, 30.0),
                (87.686, 30.0),
                (88.827, 30.0),
                (89.968, 30.0),
                (91.11, 30.0),
                (92.251, 30.0),
                (92.26, 30.0),
                (92.269, 29.999),
                (92.279, 29.999),
                (92.288, 29.998),
                (92.297, 29.998),
                (92.306, 29.997),
                (92.316, 29.997),
                (92.325, 29.997),
                (92.334, 29.996),
                (92.343, 29.996),
                (92.346, 29.995),
                (92.348, 29.995),
                (92.351, 29.995),
                (92.353, 29.994),
                (92.356, 29.994),
                (92.358, 29.993),
                (92.361, 29.993),
                (92.363, 29.992),
                (92.366, 29.992),
                (92.368, 29.992),
                (91.462, 28.992),
                (90.6, 27.993),
                (89.781, 26.994),
                (89.004, 25.995),
                (88.267, 24.996),
                (87.569, 23.997),
                (86.907, 22.997),
                (86.282, 21.998),
                (85.691, 20.999),
                (85.134, 20.0),
                (84.07, 20.0),
                (83.006, 20.0),
                (81.942, 20.0),
                (80.878, 20.0),
                (79.813, 20.0),
                (78.749, 20.0),
                (77.685, 20.0),
                (76.621, 20.0),
                (75.557, 20.0),
                (74.492, 20.0),
            ),
        ),
    }

    assert shape(geometry) == shape(item.geometry)


def test_sentinel2_sliver() -> None:
    use_fsspec()

    item = Item.from_file(
        test_data.get_path(
            "data-files/raster_footprint/S2A_OPER_MSI_L2A_TL_ATOS_20220620T162319_A036527_T32TLS_N04.00.json"  # noqa
        )
    )

    update_geometry_from_asset_footprint(
        item, asset_names=["R60m_B01"], simplify_tolerance=0.005, no_data=0
    )

    geometry = {
        "type": "Polygon",
        "coordinates": (
            (
                (7.772, 46.947),
                (7.815, 46.948),
                (7.836, 45.96),
                (7.428, 45.955),
                (7.535, 46.283),
                (7.578, 46.383),
                (7.772, 46.947),
            ),
        ),
    }

    assert shape(geometry) == shape(item.geometry)


def test_sentinel2_full() -> None:
    use_fsspec()

    item = Item.from_file(
        test_data.get_path(
            "data-files/raster_footprint/S2B_OPER_MSI_L2A_TL_2BPS_20220618T135630_A027590_T32TLS_N04.00.json"  # noqa
        )
    )

    update_geometry_from_asset_footprint(
        item,
        asset_names=["R60m_B01"],
    )

    geometry = {
        "type": "Polygon",
        "coordinates": (
            (
                (6.373, 46.924),
                (6.42, 45.936),
                (7.836, 45.96),
                (7.815, 46.948),
                (6.373, 46.924),
            ),
        ),
    }

    assert shape(geometry) == shape(item.geometry)


def test_landsat8() -> None:
    use_fsspec()

    item = Item.from_file(
        test_data.get_path(
            "data-files/raster_footprint/LC08_L1TP_198029_20220331_20220406_02_T1_B2.json"
            # noqa
        )
    )

    update_geometry_from_asset_footprint(
        item, asset_names=["B2"], simplify_tolerance=0.005
    )

    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [1.375, 45.667],
                [1.886, 45.58],
                [1.889, 45.406],
                [1.315, 45.399],
                [1.312, 45.483],
                [1.375, 45.667],
            ]
        ],
    }

    assert shape(geometry) == shape(item.geometry)


def test_data_footprint_precision() -> None:
    use_fsspec()

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
                (7.5, 46.3),
                (7.6, 46.3),
                (7.6, 46.6),
                (7.7, 46.6),
                (7.7, 46.9),
                (7.8, 46.9),
                (7.8, 46.0),
                (7.5, 46.0),
            ),
        ),
    }

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
    polygon = MultiPolygon(data_polygons).convex_hull

    reprojected_polygon = densify_reproject_simplify(polygon, CRS.from_epsg(32632))

    expected = shape(
        {
            "type": "Polygon",
            "coordinates": (
                (
                    (4.511, 0.0),
                    (4.511, 0.09),
                    (5.228, 0.812),
                    (5.318, 0.813),
                    (5.318, 0.722),
                    (4.601, 0.0),
                    (4.511, 0.0),
                ),
            ),
        }
    )

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
