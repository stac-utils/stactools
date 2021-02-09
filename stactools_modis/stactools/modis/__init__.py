# flake8: noqa

from stactools.modis.stac import create_item
from stactools.modis.cog import create_cogs

import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.modis import commands

    registry.register_subcommand(commands.create_modis_command)
