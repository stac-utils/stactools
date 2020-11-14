import os
from tempfile import TemporaryDirectory

import pystac

from stactools.cli.commands.copy import create_copy_command
from tests.utils import (TestCases, CliTestCase)


class CopyTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_copy_command]

    def test_copy(self):
        cat = TestCases.planet_disaster()
        item_ids = set([i.id for i in cat.get_all_items()])
        with TemporaryDirectory() as tmp_dir:
            self.run_command(['copy', cat.get_self_href(), tmp_dir])

            copy_cat = pystac.read_file(
                os.path.join(tmp_dir, 'collection.json'))
            copy_cat_ids = set([i.id for i in copy_cat.get_all_items()])

            self.assertEqual(copy_cat_ids, item_ids)
