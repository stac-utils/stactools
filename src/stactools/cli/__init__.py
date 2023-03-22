# flake8: noqa

import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry: "Registry") -> None:
    # Register subcommands

    from stactools.cli.commands import (
        add,
        add_asset,
        add_raster,
        copy,
        create,
        info,
        layout,
        lint,
        merge,
        migrate,
        summary,
        update_extent,
        update_geometry,
        validate,
        version,
    )

    registry.register_subcommand(add.create_add_command)
    registry.register_subcommand(add_asset.create_add_asset_command)
    registry.register_subcommand(add_raster.create_add_raster_command)
    registry.register_subcommand(copy.create_copy_command)
    registry.register_subcommand(create.create_create_item_command)
    registry.register_subcommand(copy.create_move_assets_command)
    registry.register_subcommand(info.create_info_command)
    registry.register_subcommand(info.create_describe_command)
    registry.register_subcommand(layout.create_layout_command)
    registry.register_subcommand(lint.create_lint_command)
    registry.register_subcommand(merge.create_merge_command)
    registry.register_subcommand(summary.create_summary_command)
    registry.register_subcommand(validate.create_validate_command)
    registry.register_subcommand(version.create_version_command)
    registry.register_subcommand(update_extent.create_update_extent_command)
    registry.register_subcommand(update_geometry.create_update_geometry_command)

    # TODO
    # registry.register_subcommand(migrate.create_migrate_command)


from stactools.cli.registry import Registry

registry = Registry()
registry.load_plugins()

__version__ = stactools.core.__version__
