def register_plugin(registry):
    # Register subcommands

    from stactools.landsat import commands

    registry.register_subcommand(commands.create_convert_command)
