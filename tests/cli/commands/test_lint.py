from typing import List, Callable

from click import Group, Command

from stactools.testing import CliTestCase

from stactools.cli.commands.lint import create_lint_command

from tests import test_data


class LintTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_lint_command]

    def test_valid_item(self) -> None:
        path = test_data.get_path("data-files/linting/20201211_223832_cs2.json")
        result = self.run_command(["lint", path])
        self.assertEqual(0, result.exit_code)

    def test_invalid_item(self) -> None:
        path = test_data.get_path("data-files/linting/core-item.json")
        result = self.run_command(["lint", path])
        self.assertEqual(1, result.exit_code)

    def test_collection_with_invalid_name(self) -> None:
        path = test_data.get_path(
            "data-files/catalogs/test-case-1/country-1/area-1-1/collection-invalid.json"
        )
        result = self.run_command(["lint", path])
        self.assertEqual(1, result.exit_code)
