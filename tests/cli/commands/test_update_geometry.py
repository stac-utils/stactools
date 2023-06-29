import shutil
from pathlib import Path

from click.testing import CliRunner
from stactools.cli.cli import cli

from tests import test_data


def test_update_geometry(tmp_path: Path) -> None:
    item_path = test_data.get_path(
        "data-files/raster_footprint/LC08_L1TP_198029_20220331_20220406_02_T1_B2.json"
    )
    asset_path = test_data.get_path(
        "data-files/raster_footprint/LC08_L1TP_198029_20220331_20220406_02_T1_B2.TIF"
    )
    item_path = shutil.copy(item_path, str(tmp_path))
    asset_path = shutil.copy(asset_path, str(tmp_path))

    runner = CliRunner()
    result = runner.invoke(cli, ["update-geometry", item_path])
    assert result.exit_code == 0
