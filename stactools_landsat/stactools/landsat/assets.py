from typing import List, Optional

import pystac
from pystac.extensions.eo import Band

from stactools.landsat.constants import (L8_SR_BANDS, L8_SP_BANDS)
from stactools.landsat.mtl_metadata import MtlMetadata


class AssetDef:
    """Holds asset defintions for L8 C2 Level 2 assets.

    If no explicit key is given, the key is the file suffix.
    """
    def __init__(self,
                 href_suffix: str,
                 media_type: str,
                 key: str,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 bands: Optional[List[Band]] = None,
                 is_sr: bool = False,
                 is_thermal: bool = False,
                 is_qa: bool = False,
                 gsd: Optional[float] = None):
        self.href_suffix = href_suffix
        self.media_type = media_type
        self.key = key or href_suffix
        self.title = title
        self.description = description
        self.gsd = gsd
        self.bands = bands
        if bands is None:
            if is_sr:
                band = L8_SR_BANDS.get(href_suffix.split('.')[0])
                if band is not None:
                    self.bands = [band]
            elif is_thermal:
                band = L8_SP_BANDS.get(href_suffix.split('.')[0])
                if band is not None:
                    self.bands = [band]
        self.is_sr = is_sr
        self.is_thermal = is_thermal
        self.is_qa = is_qa

    def get_href(self, base_href: str) -> str:
        return f"{base_href}_{self.href_suffix}"

    def add_asset(self, item: pystac.Item, mtl_metadata: MtlMetadata,
                  base_href: str) -> None:
        asset = pystac.Asset(href=self.get_href(base_href),
                             media_type=self.media_type)
        if self.title:
            asset.title = self.title
        if self.description:
            asset.description = self.description

        # common_metadata

        if self.gsd is not None:
            item.common_metadata.set_gsd(self.gsd, asset)
        else:
            if self.is_sr or self.is_qa:
                sr_grd = mtl_metadata.sr_gsd
                if item.common_metadata.gsd != sr_grd:
                    item.common_metadata.set_gsd(sr_grd, asset)
            if self.is_thermal:
                thermal_grd = mtl_metadata.thermal_gsd
                if item.common_metadata.gsd != thermal_grd:
                    item.common_metadata.set_gsd(thermal_grd, asset)

        # eo

        if self.bands:
            asset.properties["eo:bands"] = [b.to_dict() for b in self.bands]

        # projection
        if self.is_sr or self.is_qa:
            item.ext.projection.set_shape(mtl_metadata.sr_shape, asset)
            item.ext.projection.set_transform(mtl_metadata.sr_transform, asset)
        if self.is_thermal:
            item.ext.projection.set_shape(mtl_metadata.thermal_shape, asset)
            item.ext.projection.set_transform(mtl_metadata.thermal_transform,
                                              asset)

        item.add_asset(self.key, asset)


THUMBNAIL_ASSET_DEF = AssetDef(key="thumbnail",
                               href_suffix="thumb_small.jpeg",
                               title="Thumbnail image",
                               media_type=pystac.MediaType.JPEG)
PREVIEW_ASSET_DEF = AssetDef(key="reduced_resolution_browse",
                             href_suffix="thumb_large.jpeg",
                             title="Reduced resolution browse image",
                             media_type=pystac.MediaType.JPEG)
ANG_ASSET_DEF = AssetDef(
    href_suffix="ANG.txt",
    key="ANG",
    title="Angle Coefficients File",
    description=("Collection 2 Level-1 Angle Coefficients File (ANG)"),
    media_type=pystac.MediaType.TEXT)
MTL_TXT_ASSET_DEF = AssetDef(
    href_suffix="MTL.txt",
    key="MTL.txt",
    title="Product Metadata File",
    description=("Collection 2 Level-1 Product Metadata File (MTL)"),
    media_type=pystac.MediaType.TEXT)
MTL_XML_ASSET_DEF = AssetDef(
    href_suffix="MTL.xml",
    key="MTL.xml",
    title="Product Metadata File (xml)",
    description="Collection 2 Level-1 Product Metadata File (xml)",
    media_type=pystac.MediaType.XML)
MTL_JSON_ASSET_DEF = AssetDef(
    href_suffix="MTL.json",
    key="MTL.json",
    title="Product Metadata File (json)",
    description="Collection 2 Level-1 Product Metadata File (json)",
    media_type=pystac.MediaType.JSON)
QA_PIXEL_ASSET_DEF = AssetDef(
    href_suffix="QA_PIXEL.TIF",
    key="QA_PIXEL",
    title="Pixel Quality Assessment Band",
    description="Collection 2 Level-1 Pixel Quality Assessment Band",
    media_type=pystac.MediaType.COG,
    is_qa=True)
QA_RADSAT_ASSET_DEF = AssetDef(
    href_suffix="QA_RADSAT.TIF",
    key="QA_RADSAT",
    title="Radiometric Saturation Quality Assessment Band",
    description=("Collection 2 Level-1 Radiometric Saturation "
                 "Quality Assessment Band"),
    media_type=pystac.MediaType.COG,
    is_qa=True)

COMMON_ASSET_DEFS = [
    THUMBNAIL_ASSET_DEF, PREVIEW_ASSET_DEF, ANG_ASSET_DEF, MTL_TXT_ASSET_DEF,
    MTL_XML_ASSET_DEF, MTL_JSON_ASSET_DEF, QA_PIXEL_ASSET_DEF,
    QA_RADSAT_ASSET_DEF
]

# Surface reflectance assets
# These assets are contained in both Level 2 Science Product (L2SP)
# and Level 2 Surface Reflectance (L2SR) processing levels
B1_ASSET_DEF = AssetDef(
    href_suffix="SR_B1.TIF",
    key="SR_B1",
    title="Coastal/Aerosol Band (B1)",
    description=("Collection 2 Level-2 Coastal/Aerosol Band "
                 "(B1) Surface Reflectance"),
    media_type=pystac.MediaType.COG,
    is_sr=True)
B2_ASSET_DEF = AssetDef(href_suffix="SR_B2.TIF",
                        key="SR_B2",
                        title="Blue Band (B2)",
                        description=("Collection 2 Level-2 Blue Band "
                                     "(B2) Surface Reflectance"),
                        media_type=pystac.MediaType.COG,
                        is_sr=True)
B3_ASSET_DEF = AssetDef(href_suffix="SR_B3.TIF",
                        key="SR_B3",
                        title="Green Band (B3)",
                        description=("Collection 2 Level-2 Green Band "
                                     "(B3) Surface Reflectance"),
                        media_type=pystac.MediaType.COG,
                        is_sr=True)
B4_ASSET_DEF = AssetDef(href_suffix="SR_B4.TIF",
                        key="SR_B4",
                        title="Red Band (B4)",
                        description=("Collection 2 Level-2 Red Band "
                                     "(B4) Surface Reflectance"),
                        media_type=pystac.MediaType.COG,
                        is_sr=True)
B5_ASSET_DEF = AssetDef(
    href_suffix="SR_B5.TIF",
    key="SR_B5",
    title="Near Infrared Band 0.8 (B5)",
    description=("Collection 2 Level-2 Near Infrared Band 0.8 "
                 "(B5) Surface Reflectance"),
    media_type=pystac.MediaType.COG,
    is_sr=True)
B6_ASSET_DEF = AssetDef(
    href_suffix="SR_B6.TIF",
    key="SR_B6",
    title="Short-wave Infrared Band 1.6 (B6)",
    description=("Collection 2 Level-2 Short-wave Infrared Band 1.6 "
                 "(B6) Surface Reflectance"),
    media_type=pystac.MediaType.COG,
    is_sr=True)
B7_ASSET_DEF = AssetDef(
    href_suffix="SR_B7.TIF",
    key="SR_B7",
    title="Short-wave Infrared Band 2.2 (B7)",
    description=("Collection 2 Level-2 Short-wave Infrared Band 2.2 "
                 "(B7) Surface Reflectance"),
    media_type=pystac.MediaType.COG,
    is_sr=True)
QA_AEROSOL_ASSET_DEF = AssetDef(
    href_suffix="SR_QA_AEROSOL.TIF",
    key="SR_QA_AEROSOL",
    title="Aerosol Quality Analysis Band",
    description=("Collection 2 Level-2 Aerosol Quality Analysis Band "
                 "(ANG) Surface Reflectance"),
    media_type=pystac.MediaType.COG,
    is_qa=True)

SR_ASSET_DEFS = [
    B1_ASSET_DEF, B2_ASSET_DEF, B3_ASSET_DEF, B4_ASSET_DEF, B5_ASSET_DEF,
    B6_ASSET_DEF, B7_ASSET_DEF, QA_AEROSOL_ASSET_DEF
]

# Thermal assets
# These assets are contained only in the Level 2 Science Product (L2SP)
# processing level
ST_B10_ASSET_DEF = AssetDef(
    # COG has Pixel Size of 30m,
    # but 100m spatial resolution at the sensor
    gsd=100.0,
    href_suffix="ST_B10.TIF",
    key="ST_B10",
    title="Surface Temperature Band (B10)",
    description=("Landsat Collection 2 Level-2 Surface Temperature Band "
                 "(B10) Surface Temperature Product"),
    media_type=pystac.MediaType.COG,
    is_thermal=True)

ST_ATRAN_ASSET_DEF = AssetDef(
    href_suffix="ST_ATRAN.TIF",
    key="ST_ATRAN",
    title="Atmospheric Transmittance Band",
    description=("Landsat Collection 2 Level-2 Atmospheric "
                 "Transmittance Band Surface Temperature Product"),
    media_type=pystac.MediaType.COG,
    is_thermal=True)

ST_CDIST_ASSET_DEF = AssetDef(
    href_suffix="ST_CDIST.TIF",
    key="ST_CDIST",
    title="Cloud Distance Band",
    description=("Landsat Collection 2 Level-2 Cloud Distance Band "
                 "Surface Temperature Product"),
    media_type=pystac.MediaType.COG,
    is_thermal=True)

ST_DRAD_ASSET_DEF = AssetDef(
    href_suffix="ST_DRAD.tif",
    key="ST_DRAD",
    title="Downwelled Radiance Band",
    description=("Landsat Collection 2 Level-2 Downwelled "
                 "Radiance Band Surface Temperature Product"),
    media_type=pystac.MediaType.COG,
    is_thermal=True)

ST_URAD_ASSET_DEF = AssetDef(
    href_suffix="ST_URAD.TIF",
    key="ST_URAD",
    title="Upwelled Radiance Band",
    description=("Landsat Collection 2 Level-2 Upwelled "
                 "Radiance Band Surface Temperature Product"),
    media_type=pystac.MediaType.COG,
    is_thermal=True)

ST_TRAD_ASSET_DEF = AssetDef(
    href_suffix="ST_TRAD.TIF",
    key="ST_TRAD",
    title="Thermal Radiance Band",
    description=("Landsat Collection 2 Level-2 Thermal Radiance "
                 "Band Surface Temperature Product"),
    media_type=pystac.MediaType.COG,
    is_thermal=True)

ST_EMIS_ASSET_DEF = AssetDef(
    href_suffix="ST_EMIS.TIF",
    key="ST_EMIS",
    title="Emissivity Band",
    description=("Landsat Collection 2 Level-2 Emissivity Band "
                 "Surface Temperature Product"),
    media_type=pystac.MediaType.COG,
    is_thermal=True)

ST_EMSD_ASSET_DEF = AssetDef(
    href_suffix="ST_EMSD.TIF",
    key="ST_EMSD",
    title="Emissivity Standard Deviation Band",
    description=("Landsat Collection 2 Level-2 Emissivity "
                 "Standard Deviation Band Surface Temperature Product"),
    media_type=pystac.MediaType.COG,
    is_thermal=True)

ST_QA_ASSET_DEF = AssetDef(
    href_suffix="ST_QA.TIF",
    key="ST_QA",
    title="Surface Temperature Quality Assessment Band",
    description=("Landsat Collection 2 Level-2 Surface Temperature "
                 "Band Surface Temperature Product"),
    media_type=pystac.MediaType.COG,
    is_thermal=True)

THERMAL_ASSET_DEFS = [
    ST_B10_ASSET_DEF, ST_ATRAN_ASSET_DEF, ST_CDIST_ASSET_DEF,
    ST_DRAD_ASSET_DEF, ST_URAD_ASSET_DEF, ST_TRAD_ASSET_DEF, ST_EMIS_ASSET_DEF,
    ST_EMSD_ASSET_DEF, ST_QA_ASSET_DEF
]
