from collections import defaultdict
import logging
import os
import re
from subprocess import Popen, PIPE, STDOUT
from tempfile import TemporaryDirectory

import pystac
import rasterio as rio
from shapely.geometry import shape

from stactools.aster.constants import (HDF_ASSET_KEY, ASTER_BANDS)
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


def export_band(subdataset, bounds, crs, output_path):
    # ulx uly lrx lry
    ullr_args = [str(x) for x in [bounds[0], bounds[3], bounds[2], bounds[1]]]
    cmd = ['gdal_translate', '-of', 'GTiff', '-a_ullr']
    cmd += ullr_args
    cmd += ['-a_srs', crs, subdataset, output_path]
    call(cmd)


def merge_bands(input_paths, output_path):
    call(['gdal_merge.py', '-separate', '-o', output_path] + input_paths)


def cogify(input_path, output_path):
    call([
        'gdal_translate', '-of', 'COG', '-co', 'compress=deflate', input_path,
        output_path
    ])


def _create_cog(item, href, subdatasets, bands):
    geom = item.geometry
    crs = 'epsg:{}'.format(item.ext.projection.epsg)
    reprojected_geom = reproject_geom('epsg:4326', crs, geom)
    bounds = list(shape(reprojected_geom).bounds)

    with TemporaryDirectory() as tmp_dir:
        band_paths = []
        for subdataset, band in zip(subdatasets, bands):
            band_path = os.path.join(tmp_dir, '{}.tif'.format(band.name))
            export_band(subdataset, bounds, crs, band_path)
            band_paths.append(band_path)

        merged_path = os.path.join(tmp_dir, 'merged.tif')
        merge_bands(band_paths, merged_path)

        cogify(merged_path, href)

    return href


def create_cogs(item, cog_directory=None):
    """Create COGs from the HDF asset contained in the passed in STAC item.

    Args:
        item (pystac.Item): ASTER L1T 003 Item that contains an asset
            with key equal to stactools.aster.constants.HDF_ASSET_KEY,
            which will be converted to COGs.
        cog_dir (str): A URI of a directory to store COGs. This will be used
            in conjunction with the file names based on the COG asset to store
            the COG data. If not supplied, the directory of the Item's self HREF
            will be used.

    Returns:
        pystac.Item: The same item, mutated to include assets for the
            new COGs.
    """
    if cog_directory is None:
        cog_directory = os.path.dirname(item.get_self_href())

    hdf_asset = item.assets.get(HDF_ASSET_KEY)
    if hdf_asset is None:
        raise ValueError(
            'Item does not have a asset with key {}.'.format(HDF_ASSET_KEY))

    hdf_href = hdf_asset.href
    with rio.open(hdf_href) as ds:
        subdatasets = ds.subdatasets

    # Gather the subdatasets by sensor, sorted by band number
    sensor_to_subdatasets = defaultdict(list)
    for sd in subdatasets:
        m = re.search(r':?([\w]+)_Swath:ImageData([\d]+)', sd)
        if m is None:
            raise ValueError(
                'Unexpected subdataset {} - is this a non-standard ASTER L1T 003 HDF-EOS file?'
                .format(sd))
        sensor_to_subdatasets[m.group(1)].append((sd, m.group(2)))

    for k in sensor_to_subdatasets:
        sensor_to_subdatasets[k] = [
            x[0] for x in sorted(sensor_to_subdatasets[k], key=lambda x: x[1])
        ]

    sensor_to_bands = defaultdict(list)

    # Gather the bands for each sensor, sorted by band number
    for band in ASTER_BANDS:
        sensor_to_bands[band.description.split('_')[0]].append(band)
    for sensor in sensor_to_bands:
        sensor_to_bands[sensor] = sorted(
            sensor_to_bands[sensor],
            key=lambda b: re.search('([d]+)', b.description).group(1))

    # Use subdataset keys, as data might be missing some sensors.
    for sensor in sensor_to_subdatasets:
        href = os.path.join(cog_directory, '{}-cog.tif'.format(sensor))
        _create_cog(item, href, sensor_to_subdatasets[sensor],
                    sensor_to_bands[sensor])

        asset = pystac.Asset(href=href,
                             media_type=pystac.MediaType.COG,
                             roles=['data'],
                             title='{} Swath data'.format(sensor))

        item.ext.eo.set_bands(sensor_to_bands[sensor], asset)

        item.assets[sensor] = asset
