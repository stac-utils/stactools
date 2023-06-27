import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner
from stactools.cli.cli import cli

from tests import test_data


@pytest.fixture(scope="function")
def tmp_planet_disaster_path(tmp_path: Path) -> str:
    src = test_data.get_path("data-files/planet-disaster")
    dst = tmp_path / "planet-disaster"
    shutil.copytree(src, str(dst))
    return str(dst / "collection.json")


def test_migrate_no_save_by_default(tmp_planet_disaster_path: str):
    path = tmp_planet_disaster_path
    with open(path) as f:
        before = f.readlines()

    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", path])
    assert result.exit_code == 0

    with open(path) as f:
        after = f.readlines()

    assert before == after


def test_migrate_with_save(tmp_planet_disaster_path: str):
    path = tmp_planet_disaster_path
    with open(path) as f:
        before = f.readlines()

    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", path, "--save"])
    assert result.exit_code == 0

    with open(path) as f:
        after = f.readlines()

    assert before != after


def test_migrate_show_diff(tmp_planet_disaster_path: str):
    path = tmp_planet_disaster_path
    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", path, "--show-diff"])
    assert result.exit_code == 0
    assert result.output.startswith(
        """--- before

+++ after
"""
    )


def test_migrate_hide_diff(tmp_planet_disaster_path: str):
    path = tmp_planet_disaster_path
    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", path, "--hide-diff"])
    assert result.exit_code == 0
    assert not result.output
