import os.path
from tempfile import TemporaryDirectory
import unittest

from stactools.goes import Dataset
from tests.utils import TestData, validate_cloud_optimized_geotiff

EXTERNAL_DATA_PATH = (
    "goes/OR_ABI-L2-CMIPM1-M6C02_G16_s20211231619248_e20211231619306_c20211231619382.nc"
)


class DatasetTest(unittest.TestCase):
    def test_cogify(self):
        path = TestData.get_external_data(EXTERNAL_DATA_PATH)
        dataset = Dataset(path)
        with TemporaryDirectory() as directory:
            cogs = dataset.cogify(directory)

            data_path = cogs["CMI"]
            self.assertEqual(
                os.path.basename(data_path),
                os.path.splitext(os.path.basename(path))[0] + "_CMI.tif")
            warnings, errors, _ = validate_cloud_optimized_geotiff.validate(
                data_path, full_check=True)
            self.assertEqual(len(warnings), 0)
            self.assertEqual(len(errors), 0)

            dqf_path = cogs["DQF"]
            self.assertEqual(
                os.path.basename(dqf_path),
                os.path.splitext(os.path.basename(path))[0] + "_DQF.tif")
            warnings, errors, _ = validate_cloud_optimized_geotiff.validate(
                dqf_path, full_check=True)
            self.assertEqual(len(warnings), 0)
            self.assertEqual(len(errors), 0)

    def test_read_href_modifier(self):
        did_it = False

        def modify_href(href: str) -> str:
            nonlocal did_it
            did_it = True
            return href

        path = TestData.get_external_data(EXTERNAL_DATA_PATH)
        Dataset(path, read_href_modifier=modify_href)
        self.assertTrue(did_it)

    def test_cog_file_names(self):
        path = TestData.get_external_data(EXTERNAL_DATA_PATH)
        dataset = Dataset(path)
        cog_file_names = dataset.cog_file_names()
        self.assertEqual(
            set(cog_file_names),
            set([
                "OR_ABI-L2-CMIPM1-M6C02_G16_s20211231619248_e20211231619306_c20211231619382_CMI.tif",  # noqa
                "OR_ABI-L2-CMIPM1-M6C02_G16_s20211231619248_e20211231619306_c20211231619382_DQF.tif"
            ]))
