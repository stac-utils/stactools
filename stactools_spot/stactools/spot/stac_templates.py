from datetime import datetime

from pystac import (
    StacIO,
    Catalog,
    Collection,
    Extent,
    Link,
    Provider,
    SpatialExtent,
    TemporalExtent,
)

SPOT_SENSOR = {"S4": "SPOT 4", "S5": "SPOT 5"}

GeobaseCatalog = Catalog(
    id="Geobase", 
    description="STAC Catalog for Geobase", 
    title=None, 
    stac_extensions=None
)

SpotProviders = [
    Provider(
        "Government of Canada",
        "Natural Resources Canada Centre for Topographic Information",
        ["licensor", "processor"],
        "www.geobase.ca",
    ),
    Provider("Sparkgeo", "info@sparkegeo.com", ["processor", "host"], "www.sparkgeo.com"),
    Provider(
        "PCI Geomatics", "info@pci.com", ["processor", "host"], "www.pcigeomatics.com"
    ),
]

SpotExtents = Extent(
    SpatialExtent([[0.0, 0.0, 0.0, 0.0]]),
    TemporalExtent(
        [
            [
                datetime.strptime("2005-01-01", "%Y-%m-%d"),
                datetime.strptime("2010-01-01", "%Y-%m-%d"),
            ]
        ]
    ),
)

OrthoCollection = Collection(
    id="canada_spot_orthoimages",
    description="Orthoimages of Canada 2005-2010",
    extent=SpotExtents,
    title=None,
    stac_extensions=None,
    license="Proprietery",
    keywords="SPOT, Geobase, orthoimages",
    providers=SpotProviders,
)

GeobaseLicense = Link(
    "license",
    "https://open.canada.ca/en/open-government-licence-canada",
    "text",
    "Open Government Licence Canada",
)


def build_catalog():
    OrthoCollection.add_link(GeobaseLicense)
    GeobaseCatalog.add_child(OrthoCollection)
    return GeobaseCatalog
