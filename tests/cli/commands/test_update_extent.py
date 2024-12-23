from click.testing import CliRunner

from stactools.cli.cli import cli
from tests import test_data


def test_update_extent():
    path = test_data.get_path(
        "data-files/basic/country-1/area-1-1/collection.json",
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["update-extent", path])
    assert result.exit_code == 0
