import logging
import json
import os

import click
import pystac

from stactools.pointcloud.stac import create_item

logger = logging.getLogger(__name__)


def create_pointcloud_command(cli):
    """Creates a command group for commands working with
    pointclouds.
    """
    @cli.group('pointcloud',
               short_help=("Commands for working with "
                           "pointclouds."))
    def pointcloud():
        pass

    @pointcloud.command('create-item',
                        short_help="Create a STAC Item from a las or laz file")
    @click.argument('href')
    @click.argument('dst')
    @click.option('-r', '--reader', help='Override the default PDAL reader.')
    @click.option('-t',
                  '--pointcloud-type',
                  default="lidar",
                  help='Set the pointcloud type (default: lidar)')
    @click.option(
        '--compute-statistics/--no-compute-statistics',
        default=False,
        help='Compute statistics for the pointcloud (could take a while)')
    @click.option(
        '-p',
        '--providers',
        help='Path to JSON file containing array of additional providers')
    def create_item_command(href, dst, reader, pointcloud_type,
                            compute_statistics, providers):
        """Creates a STAC Item based on the header of a pointcloud.

        HREF is the pointcloud file.
        DST is directory that a STAC Item JSON file will be created
        in.
        """
        additional_providers = None
        if providers is not None:
            with open(providers) as f:
                additional_providers = [
                    pystac.Provider.from_dict(d) for d in json.load(f)
                ]

        item = create_item(href,
                           pdal_reader=reader,
                           compute_statistics=compute_statistics,
                           pointcloud_type=pointcloud_type,
                           additional_providers=additional_providers)

        item_path = os.path.join(dst, '{}.json'.format(item.id))
        item.set_self_href(item_path)
        item.validate()
        item.save_object()

    return pointcloud
