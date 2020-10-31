# flake8: noqa

import stactools.core

from stactools.planet.constants import PLANET_PROVIDER
from stactools.planet.planet_item import PlanetItem
from stactools.planet.orders import OrderManifest

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.planet import commands

    registry.register_subcommand(commands.create_planet_command)
