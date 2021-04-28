import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.landsat import commands

    registry.register_subcommand(commands.create_landsat_command)
