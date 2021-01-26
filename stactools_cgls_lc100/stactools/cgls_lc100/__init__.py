# flake8: noqa

from stactools.cgls_lc100.stac import create_item
from stactools.cgls_lc100.cog import create_cogs

import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.cgls_lc100 import commands

    registry.register_subcommand(commands.create_cgls_lc100_command)
