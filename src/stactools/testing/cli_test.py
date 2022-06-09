import logging
import unittest
from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Sequence, Union

import click
from click.testing import CliRunner, Result


class CliTestCase(unittest.TestCase, ABC):
    """A command-line interface test case."""

    def use_debug_logging(self) -> None:
        """Enable debug logging for these tests."""
        logger = logging.getLogger("stactools")
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    def setUp(self) -> None:
        """Sets up a mock cli group for testing."""

        @click.group()
        def cli() -> None:
            pass

        for create_subcommand in self.create_subcommand_functions():
            create_subcommand(cli)
        self.cli = cli

    def run_command(self, cmd: Optional[Union[str, Sequence[str]]]) -> Result:
        """Runs a command, returning its result.

        If there is output, print it to stdout.

        Args:
            cmd (str): The command to run.

        Returns:
            click.Result: The command-line invocation result.
        """
        runner = CliRunner()
        result = runner.invoke(self.cli, cmd, catch_exceptions=False)
        if result.output:
            print(result.output)
        return result

    @abstractmethod
    def create_subcommand_functions(
        self,
    ) -> List[Callable[[click.Group], click.Command]]:
        """Return list of 'create_command' functions from implementations.

        Returns:
            list[Callable[[click.Group], click.Command]]: The commands to run.
        """
        pass
