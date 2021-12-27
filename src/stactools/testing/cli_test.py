from abc import (ABC, abstractmethod)
import logging
from typing import List, Callable
import unittest

import click
from click.testing import CliRunner, Result


class CliTestCase(unittest.TestCase, ABC):

    def use_debug_logging(self) -> None:
        logger = logging.getLogger('stactools')
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    def setUp(self) -> None:

        @click.group()
        def cli() -> None:
            pass

        for create_subcommand in self.create_subcommand_functions():
            create_subcommand(cli)
        self.cli = cli

    def run_command(self, cmd: str) -> Result:
        runner = CliRunner()
        result = runner.invoke(self.cli, cmd, catch_exceptions=False)
        if result.output:
            print(result.output)
        return result

    @abstractmethod
    def create_subcommand_functions(
            self) -> List[Callable[[click.Group], click.Command]]:
        """Return list of 'create_command' functions from implementations"""
        pass
