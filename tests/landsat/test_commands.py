import datetime
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from pystac import Item, validation
from stactools.landsat.commands import create_landsat_command
from stactools.landsat.utils import (_parse_date, stac_api_to_stac,
                                     transform_mtl_to_stac,
                                     transform_stac_to_stac)
from tests.utils import CliTestCase, TestData


class LandsatTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_landsat_command]

    test_folder = Path(TestData.get_path("data-files/landsat"))
    landsat_stac_file = test_folder / "LC08_L2SR_081119_20200101_20200823_02_T2.json"
    landsat_mtl_file = test_folder / "LC08_L2SR_081119_20200101_20200823_02_T2_MTL.json"
    landsat_stac_api = (
        "https://landsatlook.usgs.gov/sat-api/collections/"
        "landsat-c2l2-sr/items/LC08_L2SR_081119_20200101_20200823_02_T2")

    @property
    def landsat_stac(self):
        with open(self.landsat_stac_file) as f:
            return json.load(f)

    @property
    def landsat_mtl(self):
        with open(self.landsat_mtl_file) as f:
            return json.load(f)

    def test_load_json(self):
        """Super lazy simple check that we are loading JSON"""
        json.dumps(self.landsat_stac, indent=2)

    def test_transform_static_stac(self):
        """Load a STAC 0.7.0 file as a dict and convert to a STAC 1.0.0.beta.2 item"""
        item = transform_stac_to_stac(Item.from_dict(self.landsat_stac))
        item.validate()

    def test_transform_dynamic_stac(self):
        """Convert a URI of a STAC 0.7.0 document to a STAC 1.0.0.beta.2 document"""
        item = stac_api_to_stac(self.landsat_stac_api)
        item.validate()

    def test_transform_mtl(self):
        """Convert a JSON MTL to a STAC 1.0.0.beta.2.
        This is not fully implemented, so it fails"""
        item = transform_mtl_to_stac(self.landsat_mtl)
        # We expect failure until it is fully implemented
        with self.assertRaises(validation.STACValidationError):
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
                'landsat-convert', '--stac', self.landsat_stac_file,
                '--enable-proj', '--dst', tmp_dir
            ])

            self.assertEqual(result.exit_code,
                             0,
                             msg='\n{}'.format(result.output))

            output_stac_file = Path(
                tmp_dir) / "LC08_L2SR_081119_20200101_20200823_02_T2.json"
            assert output_stac_file.is_file()

            # Expected failure, return code 1
            result = self.run_command([
                'landsat-convert', '--mtl', self.landsat_mtl_file,
                '--enable-proj', '--dst', tmp_dir
            ])

            self.assertEqual(result.exit_code,
                             1,
                             msg='\n{}'.format(result.output))
