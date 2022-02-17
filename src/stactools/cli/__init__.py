# flake8: noqa

import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry: 'Registry') -> None:
    # Register subcommands

    from stactools.cli.commands import (add, addraster, copy, create, info,
                                        layout, merge, migrate, version,
                                        validate)

    registry.register_subcommand(add.create_add_command)
    registry.register_subcommand(addraster.create_addraster_command)
    registry.register_subcommand(copy.create_copy_command)
    registry.register_subcommand(create.create_create_item_command)
    registry.register_subcommand(copy.create_move_assets_command)
    registry.register_subcommand(info.create_info_command)
    registry.register_subcommand(info.create_describe_command)
    registry.register_subcommand(layout.create_layout_command)
    registry.register_subcommand(merge.create_merge_command)
    registry.register_subcommand(validate.create_validate_command)
    registry.register_subcommand(version.create_version_command)

    # TODO
    # registry.register_subcommand(migrate.create_migrate_command)


from stactools.cli.registry import Registry

registry = Registry()
registry.load_plugins()

__version__ = stactools.core.__version__
