from typing import Callable, List

from click import Command, Group

from stactools.cli.commands.summary import create_summary_command
from stactools.testing.cli_test import CliTestCase
from tests import test_data


class SummaryTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_summary_command]

    def test_summary(self) -> None:
        path = test_data.get_path("data-files/planet-disaster/collection.json")
        result = self.run_command(f"summary {path}")
        self.assertEqual(0, result.exit_code)
