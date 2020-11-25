# flake8: noqa

from stactools.aster.stac import create_item
from stactools.aster.cog import create_cogs

import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.aster import commands

    registry.register_subcommand(commands.create_aster_command)
