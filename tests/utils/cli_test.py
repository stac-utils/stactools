from abc import (ABC, abstractmethod)
import unittest

import click
from click.testing import CliRunner


class CliTestCase(unittest.TestCase, ABC):
    def setUp(self):
        @click.group()
        def cli():
            pass

        for create_subcommand in self.create_subcommand_functions():
            create_subcommand(cli)
        self.cli = cli

    def run_command(self, cmd):
        runner = CliRunner()
        return runner.invoke(self.cli, cmd, catch_exceptions=False)

    @abstractmethod
    def create_subcommand_functions(self):
        """Return list of 'create_command' functions from implementations"""
        pass
