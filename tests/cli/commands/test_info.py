import pystac
from click.testing import CliRunner

from stactools.cli.cli import cli


def test_info(planet_disaster: pystac.Collection) -> None:
    collection_path = planet_disaster.get_self_href()

    runner = CliRunner()
    result = runner.invoke(cli, ["info", collection_path])
    assert result.exit_code == 0


def test_describe(planet_disaster: pystac.Collection) -> None:
    collection_path = planet_disaster.get_self_href()

    runner = CliRunner()
    result = runner.invoke(cli, ["describe", collection_path])
    assert result.exit_code == 0
