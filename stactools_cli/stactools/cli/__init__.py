# flake8: noqa

import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.cli.commands import (copy, migrate, info)

    registry.register_subcommand(copy.create_copy_command)
    registry.register_subcommand(info.create_info_command)
    registry.register_subcommand(migrate.create_migrate_command)


from stactools.cli.registry import Registry

registry = Registry()
registry.load_plugins()
