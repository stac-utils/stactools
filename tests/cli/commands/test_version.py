import pystac
from click.testing import CliRunner

import stactools
from stactools.cli.cli import cli
from stactools.core.utils.subprocess import call


def test_hello_world():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0

    assert result.output == (
        f"stactools version {stactools.core.__version__}\n"
        f"PySTAC version {pystac.__version__}\n"
        f"STAC version {pystac.version.get_stac_version()}\n"
    )


def test_entry_point():
    result = call(["stac", "version"])
    assert result == 0
