from pystac.extensions.eo import Band

HDF_ASSET_KEY = 'L1T'

ASTER_FILE_NAME_REGEX = (r'AST_L1T_(?P<start>[\d]+)_'
                         r'(?P<production>[\d]+)_'
                         r'(?P<processing>[\d]+)')

ASTER_BANDS = [
    Band.create(
        name="B01",
        description="VNIR_Band1 (visible green/yellow)",
        center_wavelength=0.56,
    ),
    Band.create(
        name="B02",
        description="VNIR_Band2 (visible red)",
        center_wavelength=0.66,
    ),
    Band.create(
        name="B3N",
        description="VNIR_Band3N (near infrared, nadir pointing)",
        center_wavelength=0.82,
    ),
    Band.create(
        name="B04",
        description="SWIR_Band4 (short-wave infrared)",
        center_wavelength=1.65,
    ),
    Band.create(
        name="B05",
        description="SWIR_Band5 (short-wave infrared)",
        center_wavelength=2.165,
    ),
    Band.create(
        name="B06",
        description="SWIR_Band6 (short-wave infrared)",
        center_wavelength=2.205,
    ),
    Band.create(
        name="B07",
        description="SWIR_Band7 (short-wave infrared)",
        center_wavelength=2.26,
    ),
    Band.create(
        name="B08",
        description="SWIR_Band8 (short-wave infrared)",
        center_wavelength=2.33,
    ),
    Band.create(
        name="B09",
        description="SWIR_Band9 (short-wave infrared)",
        center_wavelength=2.395,
    ),
    Band.create(
        name="B10",
        description="TIR_Band10 (thermal infrared)",
        center_wavelength=8.3,
    ),
    Band.create(
        name="B11",
        description="TIR_Band11 (thermal infrared)",
        center_wavelength=8.65,
    ),
    Band.create(
        name="B12",
        description="TIR_Band12 (thermal infrared)",
        center_wavelength=9.11,
    ),
    Band.create(
        name="B13",
        description="TIR_Band13 (thermal infrared)",
        center_wavelength=10.6,
    ),
    Band.create(
        name="B14",
        description="TIR_Band14 (thermal infrared)",
        center_wavelength=11.3,
    )
]
