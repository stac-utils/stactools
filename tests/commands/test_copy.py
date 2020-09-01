import unittest

import click
from click.testing import CliRunner

from stactools.cli.commands.copy import create_copy_command


class CopyTest(unittest.TestCase):
    def setUp(self):
        @click.group()
        def cli():
            pass

        create_copy_command(cli)
        self.cli = cli

    def test_copy(self):
        runner = CliRunner()
        result = runner.invoke(self.cli, [
            'copy', '/src/catalog.json', '/dst/catalog.json',
            'ABSOLUTE_PUBLISHED'
        ])
        self.assertEqual(result.exit_code, 0)

    def test_copy_fail(self):
        runner = CliRunner()
        result = runner.invoke(self.cli, [
            'copy', '/src/catalog.json', '/dst/catalog.json', 'NOT_PUBLISHED'
        ])
        self.assertNotEqual(result.exit_code, 0)
