from click.testing import CliRunner

from stactools.cli.cli import cli
from tests import test_data


def test_summary() -> None:
    path = test_data.get_path("data-files/planet-disaster/collection.json")

    runner = CliRunner()
    result = runner.invoke(cli, ["summary", path])
    assert result.exit_code == 0
