from click import echo

import pystac
from pystac.version import get_stac_version

from stactools.core import __version__
from click.core import Command, Group


def create_version_command(cli: Group) -> Command:

    @cli.command('version', short_help='Display version info.')
    def version_command() -> None:
        """Display version info
        """
        echo(f"stactools version {__version__}")
        echo(f"PySTAC version {pystac.__version__}")
        echo(f"STAC version {get_stac_version()}")

    return version_command
