import pystac
from pystac.extensions.eo import Band

NAIP_ID = 'usda-naip'
NAIP_TITLE = "NAIP: National Agriculture Imagery Program"
NAIP_DESCRIPTION = """
The National Agriculture Imagery Program (NAIP) acquires aerial imagery
during the agricultural growing seasons in the continental U.S.

NAIP projects are contracted each year based upon available funding and the
FSA imagery acquisition cycle. Beginning in 2003, NAIP was acquired on
a 5-year cycle. 2008 was a transition year, and a three-year cycle began
in 2009.

NAIP imagery is acquired at a one-meter ground sample distance (GSD) with a
horizontal accuracy that matches within six meters of photo-identifiable
ground control points, which are used during image inspection.

Older images were collected using 3 bands (Red, Green, and Blue: RGB), but
newer imagery is usually collected with an additional near-infrared band
(RGBN).
""".strip('\n')

NAIP_LICENSE = 'PDDL-1.0'

USDA_PROVIDER = pystac.Provider(
    name='USDA Farm Service Agency',
    url=('https://www.fsa.usda.gov/programs-and-services/aerial-photography'
         '/imagery-programs/naip-imagery/'),
    roles=['producer', 'licensor'])

NAIP_BANDS = [
    Band.create(name="Red", common_name='red'),
    Band.create(name="Green", common_name='green'),
    Band.create(name="Blue", common_name='blue'),
    Band.create(name="NIR", common_name='nir', description="near-infrared")
]
