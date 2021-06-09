from abc import (ABC, abstractmethod)
import logging
from typing import List, Callable
import unittest

import click
from click.testing import CliRunner


class CliTestCase(unittest.TestCase, ABC):
    def use_debug_logging(self):
        logger = logging.getLogger('stactools')
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    def setUp(self):
        @click.group()
        def cli():
            pass

        for create_subcommand in self.create_subcommand_functions():
            create_subcommand(cli)
        self.cli = cli

    def run_command(self, cmd):
        runner = CliRunner()
        result = runner.invoke(self.cli, cmd, catch_exceptions=False)
        if result.output:
            print(result.output)
        return result

    @abstractmethod
    def create_subcommand_functions(self) -> List[Callable]:
        """Return list of 'create_command' functions from implementations"""
        pass
