import datetime
import json
import os.path
from pathlib import Path
from tempfile import TemporaryDirectory

import pystac
from stactools.landsat.commands import create_landsat_command
from stactools.landsat.utils import (_parse_date, stac_api_to_stac,
                                     transform_mtl_to_stac,
                                     transform_stac_to_stac)

from tests.utils import CliTestCase, TestData

TEST_FOLDER = Path(TestData.get_path("data-files/landsat"))
ALL_EXAMPLES = [
    "LC08_L2SR_081119_20200101_20200823_02_T2_SR_stac.json",
    "LC08_L2SP_030034_20201111_20201212_02_T1_SR_stac.json",
    "LC08_L2SR_232122_20191218_20201023_02_T2_SR_stac.json",
    "LE07_L2SP_167064_20070321_20200913_02_T1_SR_stac.json",
    "LT05_L2SP_201034_19860504_20200917_02_T1_SR_stac.json",
]


class LandsatTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_landsat_command]

    landsat_stac_files = [str(TEST_FOLDER / f) for f in ALL_EXAMPLES]
    landsat_mtl_file = TEST_FOLDER / "LC08_L2SR_081119_20200101_20200823_02_T2_MTL.json"

    @property
    def landsat_stac(self):
        stac_file = pystac.Item.from_file(self.landsat_stac_files[0])
        return stac_file

    @property
    def landsat_mtl(self):
        with open(self.landsat_mtl_file) as f:
            return json.load(f)

    def test_load_json(self):
        """Super lazy simple check that we are loading JSON"""
        assert self.landsat_stac.STAC_OBJECT_TYPE == pystac.STACObjectType.ITEM

    def test_transform_static_stac(self):
        """Load a range of STAC 0.7.0 files and convert them to STAC 1.0.0.beta.2 items"""
        for stac_file in self.landsat_stac_files:
            item = transform_stac_to_stac(pystac.Item.from_file(stac_file))
            item.validate()

    def test_transform_static_stac_asset_not_available(self):
        """Raises an exception when geotiff asset isn't available"""

        for stac_file in self.landsat_stac_files:
            item = pystac.Item.from_file(stac_file)
            for asset in item.assets.values():
                # Replace a valid local file for an invalid url forcing an exception
                asset.href = asset.href.replace(
                    'LC08_L2SR_081119_20200101_20200823_02_T2_SR_B2_small.TIF',
                    "just/an/invalid/url.json")
            with self.assertRaises(pystac.STACError):
                transform_stac_to_stac(item)

    def test_transform_static_stac_missing_asset_b2_b10(self):
        """It has to be able to gather the right information from any geotiff files"""

        for stac_file in self.landsat_stac_files:
            item = pystac.Item.from_file(stac_file)

            if item.assets.get("SR_B2.TIF"):
                item.assets.pop("SR_B2.TIF")

            if item.assets.get("ST_B10.TIF"):
                item.assets.pop("ST_B10.TIF")

            item = transform_stac_to_stac(item)
            item.validate()

    def test_transform_dynamic_stac(self):
        """Convert a URI of a STAC 0.7.0 document to a STAC 1.0.0.beta.2 document"""
        item = stac_api_to_stac(self.landsat_stac_files[0])
        item.validate()

    def test_transform_mtl(self):
        """Convert a JSON MTL to a STAC 1.0.0.beta.2.
        This is not fully implemented, so it fails"""
        item = transform_mtl_to_stac(self.landsat_mtl)
        # We expect failure until it is fully implemented
        with self.assertRaises(pystac.validation.STACValidationError):
            item.validate()

    def test_date_parse(self):
        """Can we parse a simple date string?"""
        string = "2020-01-01T23:08:52.6773140Z"
        target_datetime = datetime.datetime(2020, 1, 1, 23, 8, 52, 677314,
                                            datetime.timezone.utc)

        parsed_datetime = _parse_date(string)

        assert target_datetime == parsed_datetime

    def test_converts(self):
        """Test the actual CLI application"""

        with TemporaryDirectory() as tmp_dir:
            # Expected success
            result = self.run_command([
                'landsat', 'convert', '--stac', self.landsat_stac_files[0],
                '--enable-proj', '--dst', tmp_dir
            ])

            self.assertEqual(result.exit_code,
                             0,
                             msg='\n{}'.format(result.output))

            output_stac_file = os.path.join(
                tmp_dir, "LC08_L2SR_081119_20200101_20200823_02_T2.json")
            item = pystac.Item.from_file(output_stac_file)
            self.assertEqual(item.ext.projection.epsg, 3031)
