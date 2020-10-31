import os
import unittest
from tempfile import TemporaryDirectory

import click
from click.testing import CliRunner
import pystac

from stactools.cli.commands.copy import create_copy_command
from tests.utils import TestCases


class CopyTest(unittest.TestCase):
    def setUp(self):
        @click.group()
        def cli():
            pass

        create_copy_command(cli)
        self.cli = cli

    def test_copy(self):
        cat = TestCases.planet_disaster()
        item_ids = set([i.id for i in cat.get_all_items()])
        with TemporaryDirectory() as tmp_dir:
            runner = CliRunner()
            runner.invoke(self.cli, ['copy', cat.get_self_href(), tmp_dir])

            copy_cat = pystac.read_file(
                os.path.join(tmp_dir, 'collection.json'))
            copy_cat_ids = set([i.id for i in copy_cat.get_all_items()])

            self.assertEqual(copy_cat_ids, item_ids)
