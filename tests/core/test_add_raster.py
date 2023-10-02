import tempfile
from typing import Callable, List, Optional

import numpy as np
import pystac
import pytest
import rasterio
from rasterio.crs import CRS
from rasterio.transform import Affine
from stactools.core import create
from stactools.core.add_raster import add_raster_to_item


def random_data(count: int) -> np.ndarray:
    return np.random.rand(count, 10, 10) * 10


def nan_data(count: int) -> np.ndarray:
    data = np.empty((count, 10, 10))
    data[:] = np.nan
    return data


def data_with_nan(count: int) -> np.ndarray:
    data = np.random.rand(count, 10, 10) * 10
    data[0][1][1] = np.nan
    return data


def zero_data(count: int) -> np.ndarray:
    return np.zeros((count, 10, 10))


def test_add_raster(tmp_asset_path) -> None:
    item = create.item(tmp_asset_path)
    add_raster_to_item(item)

    asset: pystac.Asset = item.assets["data"]

    _assert_asset(
        asset,
        expected_count=1,
        expected_nodata=None,
        expected_spatial_resolution=60.0,
        expected_dtype=np.dtype("uint8"),
        expected_min=[74.0],
        expected_max=[255.0],
    )


@pytest.mark.parametrize(
    "count,nodata,dtype,datafunc,hist_count",
    [
        (1, 0, np.dtype("int8"), random_data, 256),
        (1, None, np.dtype("float64"), random_data, 256),
        (1, np.nan, np.dtype("float64"), random_data, 256),
        (2, 0, np.dtype("int8"), random_data, 256),
        (2, None, np.dtype("float64"), random_data, 256),
        (2, np.nan, np.dtype("float64"), random_data, 256),
        (1, 0, np.dtype("uint8"), zero_data, 0),
        (1, None, np.dtype("uint8"), zero_data, 256),
        (1, None, np.dtype("float64"), nan_data, 0),
        (1, np.nan, np.dtype("float64"), nan_data, 0),
        (1, None, np.dtype("float64"), data_with_nan, 256),
        (1, np.nan, np.dtype("float64"), data_with_nan, 256),
    ],
)
def test_add_raster_with_nodata(
    count: int, nodata: float, dtype: np.dtype, datafunc: Callable, hist_count: int
) -> None:
    with tempfile.NamedTemporaryFile(suffix=".tif") as tmpfile:
        with rasterio.open(
            tmpfile.name,
            mode="w",
            driver="GTiff",
            count=count,
            nodata=nodata,
            dtype=dtype,
            transform=Affine(0.1, 0.0, 1.0, 0.0, -0.1, 1.0),
            width=10,
            height=10,
            crs=CRS.from_epsg(4326),
        ) as dst:
            data = datafunc(count)
            data.astype(dtype)
            dst.write(data)

        with rasterio.open(tmpfile.name) as src:
            data = src.read(masked=True)
            minimum = []
            maximum = []
            for i, _ in enumerate(src.indexes):
                minimum.append(float(np.nanmin(data[i])))
                maximum.append(float(np.nanmax(data[i])))

        item = create.item(tmpfile.name)

        add_raster_to_item(item)

        asset: pystac.Asset = item.assets["data"]
        _assert_asset(
            asset,
            expected_count=count,
            expected_nodata=nodata,
            expected_spatial_resolution=0.1,
            expected_dtype=dtype,
            expected_min=minimum,
            expected_max=maximum,
            expected_hist_count=hist_count,
        )


def test_add_raster_without_stats(tmp_asset_path) -> None:
    item = create.item(tmp_asset_path)
    add_raster_to_item(item, statistics=False)

    asset: pystac.Asset = item.assets["data"]
    bands = asset.extra_fields.get("raster:bands")

    assert bands[0].get("statistics") is None
    assert bands[0].get("histogram")


def test_add_raster_without_histogram(tmp_asset_path) -> None:
    item = create.item(tmp_asset_path)
    add_raster_to_item(item, histogram=False)

    asset: pystac.Asset = item.assets["data"]
    bands = asset.extra_fields.get("raster:bands")

    assert bands[0].get("statistics")
    assert bands[0].get("histogram") is None


def _assert_asset(
    asset: pystac.Asset,
    expected_count: int,
    expected_nodata: Optional[float],
    expected_dtype: np.dtype,
    expected_spatial_resolution: float,
    expected_min: List[float],
    expected_max: List[float],
    expected_hist_count=256,
) -> None:
    bands = asset.extra_fields.get("raster:bands")
    assert bands
    assert len(bands) == expected_count

    for i, band in enumerate(bands):
        nodata = band.get("nodata")
        dtype = band["data_type"].value
        spatial_resolution = band["spatial_resolution"]
        statistics = band["statistics"]
        histogram = band["histogram"]
        assert nodata == expected_nodata or (
            np.isnan(nodata) and np.isnan(expected_nodata)
        )
        assert dtype == expected_dtype.name
        assert spatial_resolution == expected_spatial_resolution
        assert statistics == {
            "minimum": expected_min[i],
            "maximum": expected_max[i],
        } or (
            np.isnan(statistics["maximum"])
            and np.isnan(expected_max[i])
            and np.isnan(statistics["minimum"])
            and np.isnan(expected_min[i])
        )
        assert histogram["count"] == expected_hist_count
        assert histogram["max"] == band["statistics"]["maximum"] or (
            np.isnan(histogram["max"]) and np.isnan(statistics["maximum"])
        )
        assert histogram["min"] == band["statistics"]["minimum"] or (
            np.isnan(histogram["min"]) and np.isnan(statistics["minimum"])
        )
        assert len(histogram["buckets"]) == histogram["count"]
