from typing import Callable, List

from click import Command, Group
from stactools.cli.commands.validate import create_validate_command
from stactools.testing.cli_test import CliTestCase

from tests import test_data


class ValidatateTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_validate_command]

    def test_valid_item(self) -> None:
        path = test_data.get_path(
            "data-files/catalogs/test-case-1/country-1/area-1-1/"
            "area-1-1-imagery/area-1-1-imagery.json"
        )
        result = self.run_command(f"validate {path} --no-validate-assets")
        self.assertEqual(0, result.exit_code)

    def test_invalid_item(self) -> None:
        path = test_data.get_path(
            "data-files/catalogs/test-case-1/country-1/area-1-1/"
            "area-1-1-imagery/area-1-1-imagery-invalid.json"
        )
        result = self.run_command(f"validate {path}")
        self.assertEqual(1, result.exit_code)

    def test_collection_with_invalid_item(self) -> None:
        path = test_data.get_path(
            "data-files/catalogs/test-case-1/country-1/area-1-1/collection-invalid.json"
        )
        result = self.run_command(f"validate {path}")
        self.assertEqual(1, result.exit_code)

    def test_collection_with_invalid_item_no_validate_all(self) -> None:
        path = test_data.get_path(
            "data-files/catalogs/test-case-1/country-1/area-1-1/collection-invalid.json"
        )
        result = self.run_command(f"validate {path} --no-recursive")
        self.assertEqual(0, result.exit_code)

    def test_collection_invalid_asset(self) -> None:
        path = test_data.get_path(
            "data-files/catalogs/test-case-1/country-1"
            "/area-1-1/area-1-1-imagery/area-1-1-imagery.json"
        )
        result = self.run_command(f"validate {path}")
        self.assertEqual(
            0, result.exit_code
        )  # unreachable links aren't an error in stac-validator
