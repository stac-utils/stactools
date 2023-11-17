import pytest
from click.testing import CliRunner
from stactools.cli.cli import cli

from tests import test_data

pytest.importorskip("stac_check")


def test_valid_item() -> None:
    path = test_data.get_path("data-files/linting/20201211_223832_cs2.json")

    runner = CliRunner()
    result = runner.invoke(cli, ["lint", path])
    assert result.exit_code == 0


def test_invalid_item() -> None:
    path = test_data.get_path("data-files/linting/core-item.json")

    runner = CliRunner()
    result = runner.invoke(cli, ["lint", path])
    assert result.exit_code == 1


def test_collection_with_invalid_name() -> None:
    path = test_data.get_path(
        "data-files/basic/country-1/area-1-1/collection-invalid.json"
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["lint", path])
    assert result.exit_code == 1
