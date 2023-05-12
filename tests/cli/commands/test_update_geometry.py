import shutil
from tempfile import TemporaryDirectory
from typing import Callable, List

from click import Command, Group
from stactools.cli.commands.update_geometry import create_update_geometry_command
from stactools.testing.cli_test import CliTestCase

from tests import test_data


class UpdateGeometryTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_update_geometry_command]

    def test_update_geometry(self) -> None:
        item_path = test_data.get_path(
            "data-files/raster_footprint/LC08_L1TP_198029_20220331_20220406_02_T1_B2.json"
        )
        asset_path = test_data.get_path(
            "data-files/raster_footprint/LC08_L1TP_198029_20220331_20220406_02_T1_B2.TIF"
        )
        with TemporaryDirectory() as temporary_directory:
            item_path = shutil.copy(item_path, temporary_directory)
            asset_path = shutil.copy(asset_path, temporary_directory)
            result = self.run_command(f"update-geometry {item_path}")
            assert result.exit_code == 0
