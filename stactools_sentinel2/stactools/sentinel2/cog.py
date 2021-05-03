import logging
import os
import shutil
from tempfile import TemporaryDirectory

import pystac
from pystac.utils import make_absolute_href

from stactools.core.utils.subprocess import call
from stactools.core.utils.convert import cogify

logger = logging.getLogger(__name__)

# TODO: Refactor this into general-purpose cogification of item asset
# Currently does not allow the specification of specific assets to cogify.


def create_cogs(item):
    cog_directory = os.path.join(os.path.dirname(item.get_self_href()), "cog")
    if not os.path.exists(cog_directory):
        os.makedirs(cog_directory)

    asset_tuples = list(item.assets.items())
    [
        item.add_asset(*create_cog_asset(key, asset, cog_directory))
        for (key, asset) in asset_tuples if is_non_cog_image(asset)
    ]


def create_cog_asset(key, asset, path):
    asset_filename, extension = os.path.splitext(os.path.split(asset.href)[1])
    cog_filename = f'{asset_filename}-COG.tif'
    cog_path = os.path.join(path, cog_filename)

    with TemporaryDirectory() as tmp_dir:
        reprojected_path = os.path.join(tmp_dir, f'reprojected{extension}')
        print(f'reprojecting {asset.href}')
        reproject(asset.href, reprojected_path)
        print(f'cogifying {asset.href}')
        cogify(reprojected_path, cog_path)
        shutil.rmtree(tmp_dir, ignore_errors=True)

    asset = pystac.Asset(href=make_absolute_href(cog_path),
                         media_type=pystac.MediaType.COG,
                         roles=['data'],
                         title=f'{asset.title} (COG)',
                         properties=asset.properties)
    return (f'{key}-cog', asset)


def is_non_cog_image(asset):
    return asset.media_type != pystac.MediaType.COG and (
        asset.media_type == pystac.MediaType.GEOTIFF
        or asset.media_type == pystac.MediaType.JPEG2000)


def reproject(input_path, output_path):
    call(['gdalwarp', '-t_srs', 'epsg:3857', input_path, output_path])
