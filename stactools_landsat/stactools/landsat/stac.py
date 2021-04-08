from typing import Optional
import pystac

from stactools.core.io import ReadHrefModifier
from stactools.landsat.assets import (ANG_ASSET_DEF, COMMON_ASSET_DEFS,
                                      SR_ASSET_DEFS, THERMAL_ASSET_DEFS)
from stactools.landsat.constants import (L8_EXTENSION_SCHEMA, L8_INSTRUMENTS,
                                         L8_ITEM_DESCRIPTION, L8_PLATFORM)
from stactools.landsat.mtl_metadata import MtlMetadata
from stactools.landsat.ang_metadata import AngMetadata


def create_stac_item(
        mtl_xml_href: str,
        read_href_modifier: Optional[ReadHrefModifier] = None) -> pystac.Item:
    """Creates a Landsat 8 C2 L2 STAC Item.

    Reads data from a single scene of
    Landsat Collection 2 Level-2 Surface Reflectance Product data.

    Uses the MTL XML HREF as the bases for other files; assumes that all
    files are co-located in a directory or blob prefix.
    """
    base_href = '_'.join(mtl_xml_href.split('_')[:-1])  # Remove the _MTL.txt

    mtl_metadata = MtlMetadata.from_file(mtl_xml_href, read_href_modifier)

    ang_href = ANG_ASSET_DEF.get_href(base_href)
    ang_metadata = AngMetadata.from_file(ang_href, read_href_modifier)

    scene_datetime = mtl_metadata.scene_datetime

    item = pystac.Item(id=mtl_metadata.scene_id,
                       bbox=mtl_metadata.bbox,
                       geometry=ang_metadata.get_scene_geometry(
                           mtl_metadata.bbox),
                       datetime=scene_datetime,
                       properties={})

    item.common_metadata.platform = L8_PLATFORM
    item.common_metadata.instruments = L8_INSTRUMENTS
    item.common_metadata.description = L8_ITEM_DESCRIPTION

    # eo
    item.ext.enable('eo')
    item.ext.eo.cloud_cover = mtl_metadata.cloud_cover

    # view
    item.ext.enable('view')
    item.ext.view.off_nadir = mtl_metadata.off_nadir
    item.ext.view.sun_elevation = mtl_metadata.sun_elevation
    # Sun Azimuth in landsat metadata is -180 to 180 from north, west being negative.
    # In STAC, it's 0 to 360 clockwise from north.
    sun_azimuth = mtl_metadata.sun_azimuth
    if sun_azimuth < 0.0:
        sun_azimuth = 360 + sun_azimuth
    item.ext.view.sun_azimuth = sun_azimuth

    # projection
    item.ext.enable('projection')
    item.ext.projection.epsg = mtl_metadata.epsg
    item.ext.projection.bbox = mtl_metadata.proj_bbox

    # landsat8
    item.stac_extensions.append(L8_EXTENSION_SCHEMA)
    item.properties.update(**mtl_metadata.additional_metadata)
    item.properties['landsat8:scene_id'] = ang_metadata.scene_id

    # -- Add assets

    # Add common assets
    for asset_definition in COMMON_ASSET_DEFS:
        asset_definition.add_asset(item, mtl_metadata, base_href)

    # Add SR assets
    for asset_definition in SR_ASSET_DEFS:
        asset_definition.add_asset(item, mtl_metadata, base_href)

    # Add thermal assets, if this is a L2SP product
    if mtl_metadata.processing_level == 'L2SP':
        for asset_definition in THERMAL_ASSET_DEFS:
            asset_definition.add_asset(item, mtl_metadata, base_href)

    # -- Add links

    usgs_item_page = (
        f"https://landsatlook.usgs.gov/stac-browser/collection02/level-2/standard/oli-tirs"
        f"/{scene_datetime.year}"
        f"/{mtl_metadata.wrs_path}/{mtl_metadata.wrs_row}"
        f"/{mtl_metadata.scene_id}")

    item.add_link(
        pystac.Link(rel="alternate",
                    target=usgs_item_page,
                    title="USGS stac-browser page",
                    media_type="text/html"))

    return item
