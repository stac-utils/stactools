import pytest
from click.testing import CliRunner
from stactools.cli.cli import cli

from tests import test_data


def test_valid_item() -> None:
    path = test_data.get_path(
        "data-files/basic/country-1/area-1-1/" "area-1-1-imagery/area-1-1-imagery.json"
    )
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "validate",
            path,
            "--no-validate-assets",
        ],
    )
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "path",
    [
        (
            "data-files/basic/country-1/area-1-1/"
            "area-1-1-imagery/area-1-1-imagery-invalid.json"
        ),
        "data-files/basic/country-1/area-1-1/collection-invalid.json",
    ],
)
def test_invalid(path: str) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", test_data.get_path(path)])
    assert result.exit_code == 1


def test_collection_invalid_asset() -> None:
    path = test_data.get_path(
        "data-files/basic/country-1" "/area-1-1/area-1-1-imagery/area-1-1-imagery.json"
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", path])
    assert result.exit_code == 0, "Unreachable links aren't an error"
