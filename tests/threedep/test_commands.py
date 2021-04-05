import os.path
from tempfile import TemporaryDirectory

import pystac

from stactools.threedep.commands import create_threedep_command
from tests.utils import CliTestCase, TestData


class CreateCollectionTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_threedep_command]

    def test_create_collection(self):
        path = TestData.get_path("data-files/threedep/base")
        with TemporaryDirectory() as directory:
            result = self.run_command([
                "threedep", "create-catalog", directory, "--id", "n41w106",
                "--id", "n40w106", "--quiet", "--source", path
            ])
            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))
            catalog = pystac.read_file(os.path.join(directory, "catalog.json"))
            item_ids = set([item.id for item in catalog.get_all_items()])
            self.assertEqual(
                item_ids,
                set(["n40w106-1", "n40w106-13", "n41w106-1", "n41w106-13"]))
