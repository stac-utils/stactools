import json

from click.testing import CliRunner

from stactools.cli.cli import cli
from tests import test_data


def test_create_item():
    path = test_data.get_path("data-files/core/byte.tif")
    runner = CliRunner()
    result = runner.invoke(cli, ["create-item", path])
    assert result.exit_code == 0
    d = json.loads(result.output)
    assert list(d["assets"].keys()) == ["data"]


def test_create_item_with_asset_key():
    path = test_data.get_path("data-files/core/byte.tif")
    runner = CliRunner()
    result = runner.invoke(cli, ["create-item", path, "foo"])
    assert result.exit_code == 0
    d = json.loads(result.output)
    assert list(d["assets"].keys()) == ["foo"]


def test_create_item_with_asset_roles():
    path = test_data.get_path("data-files/core/byte.tif")
    runner = CliRunner()
    result = runner.invoke(cli, ["create-item", path, "-r", "reference"])
    assert result.exit_code == 0
    d = json.loads(result.output)
    assert d["assets"]["data"]["roles"] == ["reference"]
