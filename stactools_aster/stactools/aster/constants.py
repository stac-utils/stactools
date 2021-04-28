from pystac.extensions.eo import Band

import re

HDF_ASSET_KEY = 'hdf'
XML_ASSET_KEY = 'xml'
VNIR_BROWSE_ASSET_KEY = 'vnir-browse'
TIR_BROWSE_ASSET_KEY = 'tir-browse'
QA_BROWSE_ASSET_KEY = 'qa-browse'
QA_TXT_ASSET_KEY = "qa-txt"

ASTER_FILE_NAME_REGEX = re.compile(r'AST_L1T_(?P<start>[\d]+)_'
                                   r'(?P<production>[\d]+)_'
                                   r'(?P<processing>[\d]+)')

ASTER_PLATFORM = "terra"
ASTER_INSTRUMENT = "aster"

VNIR_SENSOR = 'VNIR'
SWIR_SENSOR = 'SWIR'
TIR_SENSOR = 'TIR'

ASTER_SENSORS = [VNIR_SENSOR, SWIR_SENSOR, TIR_SENSOR]

ASTER_BANDS = [
    Band.create(name="VNIR_Band1",
                common_name="yellow/green",
                description="visible yellow/",
                center_wavelength=0.56,
                full_width_half_max=0.08),
    Band.create(name="VNIR_Band2",
                common_name="red",
                description="visible red",
                center_wavelength=0.66,
                full_width_half_max=0.06),
    Band.create(name="VNIR_Band3N",
                common_name="near infrared",
                description="near infrared",
                center_wavelength=0.82,
                full_width_half_max=0.08),
    Band.create(name="SWIR_Band4",
                common_name="swir",
                description="short-wave infrared",
                center_wavelength=1.65,
                full_width_half_max=0.100),
    Band.create(name="SWIR_Band5",
                common_name="swir",
                description="short-wave infrared",
                center_wavelength=2.165,
                full_width_half_max=0.040),
    Band.create(name="SWIR_Band6",
                common_name="swir",
                description="short-wave infrared",
                center_wavelength=2.205,
                full_width_half_max=0.040),
    Band.create(name="SWIR_Band7",
                common_name="swir",
                description="short-wave infrared",
                center_wavelength=2.260,
                full_width_half_max=0.050),
    Band.create(name="SWIR_Band8",
                common_name="swir",
                description="short-wave infrared",
                center_wavelength=2.339,
                full_width_half_max=0.070),
    Band.create(name="SWIR_Band9",
                common_name="swir",
                description="short-wave infrared",
                center_wavelength=2.395,
                full_width_half_max=0.070),
    Band.create(name="TIR_Band10",
                common_name="lwir",
                description="thermal infrared",
                center_wavelength=8.300,
                full_width_half_max=0.350),
    Band.create(name="TIR_Band11",
                description="thermal infrared",
                center_wavelength=8.650,
                full_width_half_max=0.350),
    Band.create(name="TIR_Band12",
                common_name="lwir",
                description="thermal infrared",
                center_wavelength=9.110,
                full_width_half_max=0.350),
    Band.create(name="TIR_Band13",
                common_name="lwir",
                description="thermal infrared",
                center_wavelength=10.600,
                full_width_half_max=0.700),
    Band.create(name="TIR_Band14",
                common_name="lwir",
                description="thermal infrared",
                center_wavelength=11.300,
                full_width_half_max=0.700)
]

# ASTER properties

UPPER_LEFT_QUAD_CLOUD_COVER = "aster:upper_left_quad_cloud_cover"
UPPER_RIGHT_QUAD_CLOUD_COVER = "aster:upper_right_quad_cloud_cover"
LOWER_LEFT_QUAD_CLOUD_COVER = "aster:lower_left_quad_cloud_cover"
LOWER_RIGHT_QUAD_CLOUD_COVER = "aster:lower_right_quad_cloud_cover"
