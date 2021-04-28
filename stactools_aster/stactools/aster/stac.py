import logging
import os
from typing import Optional

import pystac
import rasterio as rio

from stactools.core.io import ReadHrefModifier
from stactools.aster.constants import (
    ASTER_INSTRUMENT, ASTER_PLATFORM, ASTER_SENSORS, HDF_ASSET_KEY,
    ASTER_BANDS, QA_BROWSE_ASSET_KEY, QA_TXT_ASSET_KEY, SWIR_SENSOR,
    TIR_BROWSE_ASSET_KEY, TIR_SENSOR, VNIR_SENSOR, VNIR_BROWSE_ASSET_KEY,
    XML_ASSET_KEY)
from stactools.aster.xml_metadata import XmlMetadata
from stactools.aster.utils import (AsterSceneId, get_sensors_to_bands)

logger = logging.getLogger(__name__)

ASTER_PROVIDER = pystac.Provider(
    name='NASA LP DAAC at the USGS EROS Center',
    url='https://doi.org/10.5067/ASTER/AST_L1T.003',
    roles=['producer', 'processor', 'licensor'])


def _add_cog_assets(
        item: pystac.Item,
        xml_metadata: XmlMetadata,
        vnir_cog_href: Optional[str],
        swir_cog_href: Optional[str],
        tir_cog_href: Optional[str],
        read_href_modifier: Optional[ReadHrefModifier] = None) -> None:

    pointing_angles = xml_metadata.pointing_angles

    sensors_to_hrefs = {
        VNIR_SENSOR: vnir_cog_href,
        SWIR_SENSOR: swir_cog_href,
        TIR_SENSOR: tir_cog_href
    }

    def title_for(sensor):
        return f'{sensor} Swath data'

    sensors_to_bands = get_sensors_to_bands()

    for sensor in ASTER_SENSORS:
        if sensors_to_hrefs[sensor] is None:
            logger.warning(f'Skipping {sensor} COG')
            continue

        cog_href = sensors_to_hrefs[sensor]
        sensor_asset = pystac.Asset(href=cog_href,
                                    media_type=pystac.MediaType.COG,
                                    roles=['data'],
                                    title=title_for(sensor))

        # Set bands
        item.ext.eo.set_bands(sensors_to_bands[sensor], sensor_asset)

        # Set view off_nadir
        if sensor in pointing_angles:
            item.ext.view.off_nadir = abs(pointing_angles[sensor])

        # Open COG headers to get proj info
        cog_read_href = cog_href
        if read_href_modifier:
            cog_read_href = read_href_modifier(cog_read_href)

        with rio.open(cog_read_href) as ds:
            image_shape = list(ds.shape)
            proj_bbox = list(ds.bounds)
            transform = list(ds.transform)

            item.ext.projection.set_shape(image_shape, sensor_asset)
            item.ext.projection.set_bbox(proj_bbox, sensor_asset)
            item.ext.projection.set_transform(transform, sensor_asset)

        item.add_asset(sensor, sensor_asset)


def create_item(xml_href: str,
                vnir_cog_href: Optional[str],
                swir_cog_href: Optional[str],
                tir_cog_href: Optional[str],
                hdf_href: Optional[str] = None,
                vnir_browse_href: Optional[str] = None,
                tir_browse_href: Optional[str] = None,
                qa_browse_href: Optional[str] = None,
                qa_txt_href: Optional[str] = None,
                additional_providers=None,
                read_href_modifier: Optional[ReadHrefModifier] = None):
    """Creates and item from ASTER Assets."""

    if vnir_cog_href is None and \
        swir_cog_href is None and \
            tir_cog_href is None and \
            hdf_href is None:
        raise ValueError('Need to supply at least one data asset.')

    file_name = os.path.basename(xml_href)
    scene_id = AsterSceneId.from_path(file_name)

    xml_metadata = XmlMetadata.from_file(xml_href, read_href_modifier)

    geom, bounds = xml_metadata.geometries
    datetime = xml_metadata.item_datetime

    item = pystac.Item(
        id=scene_id.item_id,
        geometry=geom,
        bbox=bounds,
        datetime=datetime,
        properties={'aster:processing_number': scene_id.processing_number})

    # Common metadata
    item.common_metadata.providers = [ASTER_PROVIDER]
    if additional_providers is not None:
        item.common_metadata.providers.extend(additional_providers)
    item.common_metadata.created = xml_metadata.created
    item.common_metadata.platform = ASTER_PLATFORM
    item.common_metadata.instruments = [ASTER_INSTRUMENT]

    # eo
    item.ext.enable('eo')
    item.ext.eo.cloud_cover = xml_metadata.cloud_cover

    # sat
    item.ext.enable('sat')
    item.ext.sat.orbit_state = xml_metadata.orbit_state

    # view
    item.ext.enable('view')
    item.ext.view.sun_azimuth = xml_metadata.sun_azimuth
    sun_elevation = xml_metadata.sun_elevation
    # Sun elevation can be negative; if so, will break validation; leave out.
    # See https://github.com/radiantearth/stac-spec/issues/853
    # This is fixed in 1.0.0-RC1; store as an aster property
    #  to be updated once upgrade to 1.0.0-RC1 happens.
    if sun_elevation >= 0.0:
        item.ext.view.sun_elevation = sun_elevation
    else:
        item.ext.view.sun_elevation = 0.0
        item.properties['aster:sun_elevation'] = str(sun_elevation)

    # proj
    item.ext.enable('projection')
    item.ext.projection.epsg = xml_metadata.epsg

    # ASTER-specific properties
    item.properties.update(xml_metadata.aster_properties)

    # -- ASSETS

    # Create XML asset
    item.add_asset(
        XML_ASSET_KEY,
        pystac.Asset(href=xml_href,
                     media_type=pystac.MediaType.XML,
                     roles=['metadata'],
                     title='XML metadata'))

    # Create Assets for each of VIR, SWIR, and TIR
    _add_cog_assets(item=item,
                    xml_metadata=xml_metadata,
                    vnir_cog_href=vnir_cog_href,
                    swir_cog_href=swir_cog_href,
                    tir_cog_href=tir_cog_href,
                    read_href_modifier=read_href_modifier)

    # Create HDF EOS asset, if available
    if hdf_href is not None:
        hdf_asset = pystac.Asset(href=hdf_href,
                                 media_type=pystac.MediaType.HDF,
                                 roles=['data'],
                                 title="ASTER L1T 003 HDF-EOS")

        item.ext.eo.set_bands(ASTER_BANDS, hdf_asset)

        item.add_asset(HDF_ASSET_KEY, hdf_asset)

    # Create assets for browse files, if available
    if vnir_browse_href is not None:
        item.add_asset(
            VNIR_BROWSE_ASSET_KEY,
            pystac.Asset(href=vnir_browse_href,
                         media_type=pystac.MediaType.JPEG,
                         roles=['thumbnail'],
                         title="VNIR browse file",
                         description='Standalone reduced resolution VNIR'))

    if tir_browse_href is not None:
        item.add_asset(
            TIR_BROWSE_ASSET_KEY,
            pystac.Asset(href=tir_browse_href,
                         media_type=pystac.MediaType.JPEG,
                         roles=['thumbnail'],
                         title='Standalone reduced resolution TIR'))

    if qa_browse_href is not None:
        item.add_asset(
            QA_BROWSE_ASSET_KEY,
            pystac.Asset(
                href=qa_browse_href,
                media_type=pystac.MediaType.JPEG,
                roles=['thumbnail'],
                title='QA browse file',
                description=(
                    "Single-band black and white reduced resolution browse "
                    "overlaid with red, green, and blue (RGB) markers for GCPs "
                    "used during the geometric verification quality check.")))

    # Create an asset for the QA text report, if available
    if qa_txt_href:
        item.add_asset(
            QA_TXT_ASSET_KEY,
            pystac.Asset(href=qa_txt_href,
                         media_type=pystac.MediaType.TEXT,
                         roles=['metadata'],
                         title='QA browse file',
                         description="Geometric quality assessment report."))

    return item
