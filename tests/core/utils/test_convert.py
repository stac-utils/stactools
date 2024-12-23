from pathlib import Path

import rasterio

from stactools.core import utils
from stactools.core.utils.convert import cogify, cogify_subdatasets
from tests import test_data


def test_default(tmp_path: Path):
    infile = test_data.get_path("data-files/core/byte.tif")
    outfile = tmp_path / "byte.tif"
    cogify(infile, str(outfile))

    assert outfile.exists()
    with rasterio.open(outfile) as dataset:
        assert dataset.compression == rasterio.enums.Compression.deflate


def test_profile(tmp_path: Path):
    infile = test_data.get_path("data-files/core/byte.tif")
    outfile = tmp_path / "byte.tif"

    cogify(infile, str(outfile), profile={"compress": "lzw"})

    assert outfile.exists()
    with rasterio.open(outfile) as dataset:
        assert dataset.compression == rasterio.enums.Compression.lzw


def test_subdataset(tmp_path: Path):
    infile = test_data.get_path("data-files/hdf/AMSR_E_L3_RainGrid_B05_200707.h5")
    with utils.ignore_not_georeferenced():
        paths, names = cogify_subdatasets(infile, str(tmp_path))

    assert set(names) == {
        "MonthlyRainTotal_GeoGrid_Data_Fields_RrLandRain",
        "MonthlyRainTotal_GeoGrid_Data_Fields_TbOceanRain",
    }
    for path in paths:
        assert Path(path).exists()
        with utils.ignore_not_georeferenced():
            with rasterio.open(path) as dataset:
                assert dataset.compression == rasterio.enums.Compression.deflate
