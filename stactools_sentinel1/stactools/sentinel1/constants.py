import pystac
from pystac.link import Link
from pystac.extensions import sar
from pystac.utils import str_to_datetime
from pystac import Extent, SpatialExtent, TemporalExtent

# General Sentinel-1 Constants
# -
SENTINEL_LICENSE = Link(rel='license',
                        target='https://sentinel.esa.int/documents/' +
                        '247904/690755/Sentinel_Data_Legal_Notice')

SENTINEL_INSTRUMENTS = ['c-sar']
SENTINEL_CONSTELLATION = 'sentinel-1'
SENTINEL_PLATFORMS = ['sentinel-1a', 'sentinel-1b']
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

SENTINEL_RTC_DESCRIPTION = '''Sentinel1 radiometric terrain corrected backscatter (RTC) over CONUS. The Sentinel-1 mission is a constellation of C-band Synthetic Aperature Radar (SAR) satellites from the European Space Agency launched since 2014. These satellites collect observations of radar backscatter intensity day or night, regardless of the weather conditions, making them enormously valuable for environmental monitoring. These radar data have been processed from original Ground Range Detected (GRD) scenes into a Radiometrically Terrain Corrected, tiled product suitable for analysis. This product is available over the Contiguous United States (CONUS) since 2017 when Sentinel-1 data became globally available.'''

SENTINEL_RTC_EXTENT = Extent(SpatialExtent([-124.73460,24.54254,-66.89191,49.36949]),
                             TemporalExtent([str_to_datetime("2016-07-29T00:00:00Z"), None]))

utm_zones = ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19']
SENTINEL_RTC_EPSGS = [int(f'326{x}') for x in utm_zones]

# Item properties
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
