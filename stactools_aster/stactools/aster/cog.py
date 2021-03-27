from collections import defaultdict
import logging
import os
import re
from tempfile import TemporaryDirectory
from typing import Any, List, Tuple

import rasterio as rio
from shapely.geometry import shape

from stactools.core.projection import reproject_geom
from stactools.core.utils.subprocess import call
from stactools.aster.utils import AsterSceneId
from stactools.aster.xml_metadata import XmlMetadata

logger = logging.getLogger(__name__)


def get_cog_filename(item_id, sensor):
    return f'{item_id}-{sensor}.tif'


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


def set_band_names(href: str, band_names: List[str]) -> None:
    with rio.open(href) as ds:
        profile = ds.profile

    with rio.open(href, 'w', **profile) as ds:
        ds.descriptions = band_names


def _create_cog_for_sensor(sensor: str, file_prefix: str, tmp_dir: str,
                           output_dir: str, bounds: List[float], crs: str,
                           subdataset_info: List[Tuple[Any, int]]) -> str:
    sensor_cog_href = os.path.join(output_dir,
                                   get_cog_filename(file_prefix, sensor))

    sensor_dir = os.path.join(tmp_dir, sensor)
    os.makedirs(sensor_dir)

    band_paths = []
    band_names = []
    for subdataset, band_order in subdataset_info:
        band_path = os.path.join(sensor_dir, '{}.tif'.format(band_order))
        export_band(subdataset, bounds, crs, band_path)
        band_paths.append(band_path)
        band_names.append(f"ImageData{band_order} {sensor}_Swath")

    merged_path = os.path.join(sensor_dir, 'merged.tif')
    merge_bands(band_paths, merged_path)

    cogify(merged_path, sensor_cog_href)

    set_band_names(sensor_cog_href, band_names)

    return sensor_cog_href


def create_cogs(hdf_path: str, xml_metadata: XmlMetadata,
                output_path: str) -> None:
    """Create COGs from the HDF asset contained in the passed in STAC item.

    Args:
        hdf_path: Path to the ASTER L1T 003 HDF EOS data
        output_path: The directory to which the cogs will be written.
    """
    logger.info(f'Creating COGs and writing to {output_path}...')
    file_name = os.path.basename(hdf_path)
    aster_id = AsterSceneId.from_path(file_name)

    with rio.open(hdf_path) as ds:
        subdatasets = ds.subdatasets

    # Gather the subdatasets by sensor, sorted by band number
    sensor_to_subdatasets = defaultdict(list)
    for subdataset in subdatasets:
        m = re.search(r':?([\w]+)_Swath:ImageData([\d]+)', subdataset)
        if m is None:
            raise ValueError(
                'Unexpected subdataset {} - is this a non-standard ASTER L1T 003 HDF-EOS file?'
                .format(subdataset))
        sensor = m.group(1)
        band_order = m.group(2)
        sensor_to_subdatasets[sensor].append((subdataset, band_order))

    # Sort by band_order
    for k in sensor_to_subdatasets:
        sensor_to_subdatasets[k] = [
            x for x in sorted(sensor_to_subdatasets[k], key=lambda x: x[1])
        ]

    geom, _ = xml_metadata.geometries
    crs = 'epsg:{}'.format(xml_metadata.epsg)
    reprojected_geom = reproject_geom('epsg:4326', crs, geom)
    bounds = list(shape(reprojected_geom).bounds)

    with TemporaryDirectory() as tmp_dir:
        for sensor, subdataset_info in sensor_to_subdatasets.items():
            _create_cog_for_sensor(sensor,
                                   aster_id.file_prefix,
                                   tmp_dir=tmp_dir,
                                   output_dir=output_path,
                                   bounds=bounds,
                                   crs=crs,
                                   subdataset_info=subdataset_info)
