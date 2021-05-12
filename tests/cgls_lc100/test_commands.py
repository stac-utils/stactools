import os
from tempfile import TemporaryDirectory

import pystac

from stactools.cgls_lc100.commands import create_cgls_lc100_command
from tests.utils import (TestData, CliTestCase)

# Created from:
#
#   https://zenodo.org/record/3939050/files/
#   PROBAV_LC100_global_v3.0.1_2019-nrt_Change-Confidence-layer_EPSG-4326.tif?download=1
#
# and subsetted via `gdal_translate -projwin -180 80 -179 79`
DATA_PATH = 'data-files/cgls_lc100/PROBAV_LC100_global_v3.0.1_2019-nrt_ccl_subset.tif'


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_cgls_lc100_command]

    def test_create_item(self):
        tif_href = TestData.get_path(DATA_PATH)

        with TemporaryDirectory() as tmp_dir:
            cmd = ['cgls_lc100', 'create-item', '--cogify', tif_href, tmp_dir]
            self.run_command(cmd)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)
            cog = item.assets["cog_image"]
            self.assertTrue(os.path.exists(cog.href),
                            f"COG does not exist: {cog.href}")

        item.validate()
