import pystac
from pystac.extensions.eo import Band

NAIP_COLLECTION_NAME = 'usda-naip'
NAIP_COLLECTION_DESCRIPTION = """
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

USDA_PROVIDER = pystac.Provider(
    name='USDA Farm Service Agency',
    url=('https://www.fsa.usda.gov/programs-and-services/aerial-photography'
         '/imagery-programs/naip-imagery/'),
    roles=['producer', 'licensor'])

NAIP_BANDS = [
    Band.create(name="Red"),
    Band.create(name="Green"),
    Band.create(name="Blue"),
    Band.create(name="NIR", description="near-infrared")
]
