# flake8: noqa

import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.cli.commands import (copy, info, layout, merge, migrate,
                                        version)

    registry.register_subcommand(copy.create_copy_command)
    registry.register_subcommand(copy.create_move_assets_command)
    registry.register_subcommand(info.create_info_command)
    registry.register_subcommand(info.create_describe_command)
    registry.register_subcommand(layout.create_layout_command)
    registry.register_subcommand(merge.create_merge_command)
    registry.register_subcommand(version.create_version_command)

    # TODO
    # registry.register_subcommand(migrate.create_migrate_command)


from stactools.cli.registry import Registry

registry = Registry()
registry.load_plugins()

__version__ = stactools.core.__version__
