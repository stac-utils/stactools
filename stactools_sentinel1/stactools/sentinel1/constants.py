import pystac
from pystac.link import Link
from pystac.extensions import sar

# General Sentinel-1 Constants
# -
SENTINEL_LICENSE = Link(rel='license',
                        target='https://sentinel.esa.int/documents/' +
                        '247904/690755/Sentinel_Data_Legal_Notice')

SENTINEL_INSTRUMENTS = ['c-sar']
SENTINEL_CONSTELLATION = 'sentinel-1'
SENTINEL_FREQUENCY_BAND = sar.FrequencyBand.C
SENTINEL_CENTER_FREQUENCY = 5.405
SENTINEL_OBSERVATION_DIRECTION = sar.ObservationDirection.RIGHT

SENTINEL_PROVIDER = pystac.Provider(
    name='ESA',
    roles=['producer', 'processor', 'licensor'],
    url='https://earth.esa.int/web/guest/home')

# RTC-specific constants
# -
SENTINEL_RTC_PROVIDER = pystac.Provider(
    name='Indigo Ag Inc.',
    roles=['processor', 'licensor'],
    url='https://registry.opendata.aws/sentinel-1-rtc-indigo')

SENTINEL_RTC_LICENSE = Link(
    rel='license',
    target='https://www.indigoag.com/forms/atlas-sentinel-license')

SENTINEL_RTC_SAR = {
    'instrument_mode': 'IW',
    'product_type': 'RTC',
    'polarizations': [sar.Polarization.VV, sar.Polarization.HH],
    'resolution_range': 20.3,
    'resolution_azimuth': 22.6,
    'pixel_spacing_range': 10,
    'pixel_spacing_azimuth': 10,
    'looks_equivalent_number': 4.4,
    'looks_range': 5,
    'looks_azimuth': 1,
    'gsd': 20
}
