import pystac
from pystac.version import get_stac_version

from stactools.core import __version__
from stactools.core.utils.subprocess import call
from stactools.cli.commands.version import create_version_command

from stactools.testing import CliTestCase


class VersionTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_version_command]

    def test_hello_world(self):
        result = self.run_command(["version"])
        self.assertEqual(0, result.exit_code)
        expected = (
            f"stactools version {__version__}\n"
            f"PySTAC version {pystac.__version__}\n"
            f"STAC version {get_stac_version()}\n"
        )
        self.assertEqual(expected, result.output)

    def test_entry_point(self):
        result = call(["stac", "version"])
        self.assertEqual(0, result)
