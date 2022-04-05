from typing import Callable, List

from stactools.cli.commands.validate import create_validate_command
from stactools.testing import CliTestCase
from tests import test_data


class ValidatateTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable]:
        return [create_validate_command]

    def test_valid_item(self):
        path = test_data.get_path(
            "data-files/catalogs/test-case-1/country-1/area-1-1/"
            "area-1-1-imagery/area-1-1-imagery.json"
        )
        result = self.run_command(["validate", path, "--no-assets"])
        self.assertEqual(0, result.exit_code)

    def test_invalid_item(self):
        path = test_data.get_path(
            "data-files/catalogs/test-case-1/country-1/area-1-1/"
            "area-1-1-imagery/area-1-1-imagery-invalid.json"
        )
        result = self.run_command(["validate", path])
        self.assertEqual(1, result.exit_code)

    def test_collection_with_invalid_item(self):
        path = test_data.get_path(
            "data-files/catalogs/test-case-1/country-1/area-1-1/collection-invalid.json"
        )
        result = self.run_command(["validate", path])
        self.assertEqual(1, result.exit_code)

    def test_collection_with_invalid_item_no_validate_all(self):
        path = test_data.get_path(
            "data-files/catalogs/test-case-1/country-1/area-1-1/collection-invalid.json"
        )
        result = self.run_command(["validate", path, "--no-recurse"])
        self.assertEqual(0, result.exit_code)

    def test_collection_invalid_asset(self):
        path = test_data.get_path(
            "data-files/catalogs/test-case-1/country-1"
            "/area-1-1/area-1-1-imagery/area-1-1-imagery.json"
        )
        result = self.run_command(["validate", path])
        self.assertEqual(1, result.exit_code)
