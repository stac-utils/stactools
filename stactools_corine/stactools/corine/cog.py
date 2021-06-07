import logging
import os

import pystac

from stactools.core.utils.convert import cogify
from stactools.corine.constants import (ITEM_COG_IMAGE_NAME,
                                        ITEM_TIF_IMAGE_NAME)

logger = logging.getLogger(__name__)


def _create_cog(item, cog_directory):

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
