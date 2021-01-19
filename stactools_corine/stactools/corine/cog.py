import logging
import os
from subprocess import Popen, PIPE, STDOUT

import pystac
from shapely.geometry import shape

from stactools.corine.constants import (ITEM_COG_IMAGE_NAME,
                                        ITEM_TIF_IMAGE_NAME)
from stactools.core.projection import reproject_geom

logger = logging.getLogger(__name__)


def call(command):
    def log_subprocess_output(pipe):
        for line in iter(pipe.readline, b''):  # b'\n'-separated lines
            logger.info(line.decode("utf-8").strip('\n'))

    process = Popen(command, stdout=PIPE, stderr=STDOUT)
    with process.stdout:
        log_subprocess_output(process.stdout)
    return process.wait()  # 0 means success


def cogify(input_path, output_path):
    call([
        'gdal_translate', '-of', 'COG', '-co', 'compress=deflate', input_path,
        output_path
    ])


def _create_cog(item, cog_directory):
    geom = item.geometry
    crs = item.ext.projection.epsg
    reprojected_geom = reproject_geom('epsg:4326', crs, geom)
    bounds = shape(reprojected_geom).bounds
    print(bounds)

    tif_asset = item.assets.get(ITEM_TIF_IMAGE_NAME)
    cogify(tif_asset.href, cog_directory)

    return cog_directory


def create_cogs(item, cog_directory=None):
    """Create COGs from the HDF asset contained in the passed in STAC item.

    Args:
        item (pystac.Item): CORINE Item that contains an asset
            with key equal to stactools.corine.constants.ITEM_METADATA_NAME,
            which will be converted to COGs.
        cog_directory (str): A URI of a directory to store COGs. This will be used
            in conjunction with the file names based on the COG asset to store
            the COG data. If not supplied, the directory of the Item's self HREF
            will be used.

    Returns:
        pystac.Item: The same item, mutated to include assets for the
            new COGs.
    """
    if cog_directory is None:
        cog_directory = os.path.dirname(item.get_self_href())

    cog_href = os.path.join(cog_directory, '{}-cog.tif'.format(item.id))
    _create_cog(item, cog_href)

    asset = pystac.Asset(href=cog_href,
                         media_type=pystac.MediaType.COG,
                         roles=['data'],
                         title='Raster Dataset')

    item.assets[ITEM_COG_IMAGE_NAME] = asset
