import shutil
from pathlib import Path

import pystac
import pytest
from click.testing import CliRunner

from stactools.cli.cli import cli
from tests import test_data


@pytest.fixture(scope="function")
def tmp_planet_disaster_path(tmp_path: Path) -> str:
    src = test_data.get_path("data-files/planet-disaster-v1.0.0-beta.2")
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


def test_migrate_with_save_no_recursive(tmp_planet_disaster_path: str):
    path = tmp_planet_disaster_path
    root = pystac.Collection.from_file(path)
    child_path = next(root.get_children()).get_self_href()
    item_path = next(root.get_items(recursive=True)).get_self_href()

    with open(path) as f:
        root_before = f.readlines()

    with open(child_path) as f:
        child_before = f.readlines()

    with open(item_path) as f:
        item_before = f.readlines()

    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", path, "--save"])
    assert result.exit_code == 0

    with open(path) as f:
        root_after = f.readlines()

    with open(child_path) as f:
        child_after = f.readlines()

    with open(item_path) as f:
        item_after = f.readlines()

    assert root_before != root_after, path
    assert child_before == child_after, child_path
    assert item_before == item_after, item_path


def test_migrate_with_save_and_recursive(tmp_planet_disaster_path: str):
    path = tmp_planet_disaster_path
    root = pystac.Collection.from_file(path)
    child_path = next(root.get_children()).get_self_href()
    item_path = next(root.get_items(recursive=True)).get_self_href()

    with open(path) as f:
        root_before = f.readlines()

    with open(child_path) as f:
        child_before = f.readlines()

    with open(item_path) as f:
        item_before = f.readlines()

    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", path, "-r", "-s"])
    assert result.exit_code == 0

    with open(path) as f:
        root_after = f.readlines()

    with open(child_path) as f:
        child_after = f.readlines()

    with open(item_path) as f:
        item_after = f.readlines()

    assert root_before != root_after, path
    assert child_before != child_after, child_path
    assert item_before != item_after, item_path


def test_migrate_show_diff(tmp_planet_disaster_path: str):
    path = tmp_planet_disaster_path
    root = pystac.Collection.from_file(path)
    child_path = next(root.get_children()).get_self_href()
    item_path = next(root.get_items(recursive=True)).get_self_href()

    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", path, "--show-diff"])
    assert result.exit_code == 0

    assert result.output.startswith("--- a")
    assert path in result.output
    assert child_path not in result.output
    assert item_path not in result.output


def test_migrate_show_diff_and_recursive(tmp_planet_disaster_path: str):
    path = tmp_planet_disaster_path
    root = pystac.Collection.from_file(path)
    child_path = next(root.get_children()).get_self_href()
    item_path = next(root.get_items(recursive=True)).get_self_href()

    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", path, "--show-diff", "--recursive"])
    assert result.exit_code == 0

    assert result.output.startswith("--- a")
    assert path in result.output
    assert child_path in result.output
    assert item_path in result.output


def test_migrate_hide_diff_with_no_save_raises(tmp_planet_disaster_path: str):
    path = tmp_planet_disaster_path

    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", path, "--hide-diff"])
    assert result.exit_code == 2
    assert (
        "Error: It is only valid to use 'hide-diff' when 'save' is enabled "
        "otherwise there would be no output." in result.output
    )


def test_migrate_hide_diff(tmp_planet_disaster_path: str):
    path = tmp_planet_disaster_path

    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", path, "--hide-diff", "--save"])
    assert not result.output


def test_migrate_recursive_invalid_for_items(tmp_planet_disaster_path: str):
    path = tmp_planet_disaster_path
    root = pystac.Collection.from_file(path)
    item_path = next(root.get_items(recursive=True)).get_self_href()

    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", item_path, "-r"])
    assert result.exit_code == 2
    assert (
        "Error: 'recursive' is only a valid option for "
        "pystac.Catalogs and pystac.Collections" in result.output
    )
