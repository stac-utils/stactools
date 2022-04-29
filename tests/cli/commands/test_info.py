from typing import Callable, List

from click import Command, Group

from stactools.cli.commands.info import create_describe_command, create_info_command
from stactools.testing.cli_test import CliTestCase

from .test_cases import TestCases


class InfoTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_info_command, create_describe_command]

    def test_info(self) -> None:
        cat = TestCases.planet_disaster()
        result = self.run_command(f"info {cat.get_self_href()}")
        assert result.exit_code == 0

    def test_describe(self) -> None:
        cat = TestCases.planet_disaster()
        result = self.run_command(f"describe {cat.get_self_href()}")
        assert result.exit_code == 0
