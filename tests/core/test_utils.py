from contextlib import contextmanager
import os.path
from tempfile import TemporaryDirectory
import unittest

import rasterio

from tests.utils import TestData, validate_cloud_optimized_geotiff
from stactools.core.utils.convert import cogify


class CogifyTest(unittest.TestCase):
    @contextmanager
    def cogify(self, **kwargs):
        infile = TestData.get_path("data-files/core/byte.tif")
        with TemporaryDirectory() as directory:
            outfile = os.path.join(directory, "byte.tif")
            cogify(infile, outfile, **kwargs)
            yield outfile

    def test_default(self):
        with self.cogify() as outfile:
            self.assertTrue(os.path.exists(outfile))
            warnings, errors, _ = validate_cloud_optimized_geotiff.validate(
                outfile, full_check=True)
            self.assertEqual(len(warnings), 0)
            self.assertEqual(len(errors), 0)
            with rasterio.open(outfile) as dataset:
                self.assertEqual(dataset.compression,
                                 rasterio.enums.Compression.deflate)

    def test_override_default(self):
        with self.cogify(args=["-co", "compress=lzw"]) as outfile:
            self.assertTrue(os.path.exists(outfile))
            warnings, errors, _ = validate_cloud_optimized_geotiff.validate(
                outfile, full_check=True)
            self.assertEqual(len(warnings), 0)
            self.assertEqual(len(errors), 0)
            with rasterio.open(outfile) as dataset:
                self.assertEqual(dataset.compression,
                                 rasterio.enums.Compression.lzw)

    def test_extra_args(self):
        with self.cogify(
                extra_args=["-mo", "TIFFTAG_ARTIST=prince"]) as outfile:
            validate_cloud_optimized_geotiff.validate(outfile)
            warnings, errors, _ = validate_cloud_optimized_geotiff.validate(
                outfile, full_check=True)
            self.assertEqual(len(warnings), 0)
            self.assertEqual(len(errors), 0)
            with rasterio.open(outfile) as dataset:
                self.assertEqual(dataset.tags()["TIFFTAG_ARTIST"], "prince")
