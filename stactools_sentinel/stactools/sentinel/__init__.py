def register_plugin(registry):
    # Register subcommands

    from stactools.sentinel import commands

    registry.register_subcommand(commands.create_sentinel_command)
