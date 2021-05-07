import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.sentinel1 import commands

    registry.register_subcommand(commands.create_sentinel1_command)
