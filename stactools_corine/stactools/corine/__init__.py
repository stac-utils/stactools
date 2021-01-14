# flake8: noqa

from stactools.corine.stac import create_item
from stactools.corine.cog import create_cogs

import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.corine import commands

    registry.register_subcommand(commands.create_corine_command)
