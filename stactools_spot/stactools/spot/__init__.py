import stactools.core


stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.spot import commands

    registry.register_subcommand(commands.create_spot_command)
