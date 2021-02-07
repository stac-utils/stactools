# flake8: noqa

from stactools.naip.stac import create_item

import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.naip import commands

    registry.register_subcommand(commands.create_naip_command)
