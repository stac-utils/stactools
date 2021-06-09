from pystac.version import get_stac_version
from stactools.core.version import __version__
from stactools.cli.commands.version import create_version_command

from tests.utils import CliTestCase


class VersionTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_version_command]

    def test_hello_world(self):
        result = self.run_command(['version'])
        self.assertEqual(0, result.exit_code)
        expected = (f"stactools version {__version__}\n"
                    f"PySTAC version {get_stac_version()}\n")
        self.assertEqual(expected, result.output)
