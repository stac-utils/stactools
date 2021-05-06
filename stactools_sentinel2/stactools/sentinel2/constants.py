import pystac
from pystac.link import Link
from pystac.extensions.eo import Band

SENTINEL_LICENSE = Link(rel='license',
                        target='https://sentinel.esa.int/documents/' +
                        '247904/690755/Sentinel_Data_Legal_Notice')

SENTINEL_INSTRUMENTS = ['msi']
SENTINEL_CONSTELLATION = 'Sentinel 2'

SENTINEL_PROVIDER = pystac.Provider(
    name='ESA',
    roles=['producer', 'processor', 'licensor'],
    url='https://earth.esa.int/web/guest/home')

SAFE_MANIFEST_ASSET_KEY = "safe-manifest"
INSPIRE_METADATA_ASSET_KEY = "inspire-metadata"
PRODUCT_METADATA_ASSET_KEY = "product-metadata"
GRANULE_METADATA_ASSET_KEY = "granule-metadata"
DATASTRIP_METADATA_ASSET_KEY = "datastrip-metadata"

SENTINEL_BANDS = {
    'B01':
    Band.create(name='B01',
                common_name='coastal',
                description='Band 1 - Coastal aerosol',
                center_wavelength=0.443,
                full_width_half_max=0.027),
    'B02':
    Band.create(name='B02',
                common_name='blue',
                description='Band 2 - Blue',
                center_wavelength=0.490,
                full_width_half_max=0.098),
    'B03':
    Band.create(name='B03',
                common_name='green',
                description='Band 3 - Green',
                center_wavelength=0.560,
                full_width_half_max=0.045),
    'B04':
    Band.create(name='B04',
                common_name='red',
                description='Band 4 - Red',
                center_wavelength=0.665,
                full_width_half_max=0.038),
    'B05':
    Band.create(name='B05',
                common_name='rededge',
                description='Band 5 - Vegetation red edge 1',
                center_wavelength=0.704,
                full_width_half_max=0.019),
    'B06':
    Band.create(name='B06',
                common_name='rededge',
                description='Band 6 - Vegetation red edge 2',
                center_wavelength=0.740,
                full_width_half_max=0.018),
    'B07':
    Band.create(name='B07',
                common_name='rededge',
                description='Band 7 - Vegetation red edge 3',
                center_wavelength=0.783,
                full_width_half_max=0.028),
    'B08':
    Band.create(name='B08',
                common_name='nir',
                description='Band 8 - NIR',
                center_wavelength=0.842,
                full_width_half_max=0.145),
    'B8A':
    Band.create(name='B8A',
                common_name='rededge',
                description='Band 8A - Vegetation red edge 4',
                center_wavelength=0.865,
                full_width_half_max=0.033),
    'B09':
    Band.create(name='B09',
                description='Band 9 - Water vapor',
                center_wavelength=0.945,
                full_width_half_max=0.026),
    'B11':
    Band.create(name='B11',
                common_name='swir16',
                description='Band 11 - SWIR (1.6)',
                center_wavelength=1.610,
                full_width_half_max=0.143),
    'B12':
    Band.create(name='B12',
                common_name='swir22',
                description='Band 12 - SWIR (2.2)',
                center_wavelength=2.190,
                full_width_half_max=0.242),
}

# A dict describing the resolutions that are
# available for each band as separate assets.
# The first resolution is the sensor gsd; others
# are downscaled versions.
BANDS_TO_RESOLUTIONS = {
    'B01': [
        60,
    ],
    'B02': [
        10,
        20,
        60,
    ],
    'B03': [
        10,
        20,
        60,
    ],
    'B04': [
        10,
        20,
        60,
    ],
    'B05': [
        20,
        20,
        60,
    ],
    'B06': [
        20,
        60,
    ],
    'B07': [
        20,
        60,
    ],
    'B08': [
        10,
    ],
    'B8A': [
        20,
        60,
    ],
    'B09': [60],
    'B11': [
        20,
        60,
    ],
    'B12': [
        20,
        60,
    ],
}
