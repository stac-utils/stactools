# flake8: noqa

from pyproj import CRS
from pystac import Provider

USGS_3DEP_ID = "usgs-3dep"
THREEDEP_EPSG = 5498
THREEDEP_CRS = CRS.from_epsg(THREEDEP_EPSG)
PRODUCTS = ["1", "13"]
LICENSE = "PDDL-1.0"

DESCRIPTION = """The USGS 3D Elevation Program (3DEP) Datasets from The National Map are the primary elevation data product produced and distributed by the USGS. The 3DEP program provides a variety of resolution raster elevation data of the conterminous United States, Alaska, Hawaii, and the island territories. Some of the data sets such as the 1/3rd arc-second and 1 arc-second data set are derived from diverse source data sets that are processed to a specification with a consistent resolution, coordinate system, elevation units, and horizontal and vertical datums.  These seamless DEMs were referred to as the National Elevation Dataset (NED) from about 2000 through 2015 at which time they became the seamless DEM layers under the 3DEP program and the NED name and system were retired. Other 3DEP products include one-meter DEMs produced exclusively from high resolution light detection and ranging (lidar) source data and five-meter DEMs in Alaska as well as various source datasets including the lidar point cloud and interferometric synthetic aperture radar (Ifsar) digital surface models and intensity images. All 3DEP products are public domain. The 3DEP program is the logical result of the maturation of the long-standing USGS elevation program, which for many years concentrated on production of topographic map quadrangle-based digital elevation models. The 3DEP data  serves as the elevation layer of The National Map, and provides basic elevation information for earth science studies and mapping applications in the United States.

The seamless DEM layers under the 3DEP program are a multi-resolution dataset that is updated continuously to integrate newly available, improved elevation source data. Seamless DEM data layers under the 3DEP program  are available nationally at grid spacings of 1 arc-second (approximately 30 meters) for the conterminous United States, and at 1/3, 1/9 arc-seconds  (approximately 10 and 3 meters, respectively) and 1 meter for parts of the United States. Most seamless DEM data for Alaska is available at 2-arc-second (about 60 meters) grid spacing, where only lower resolution source data exist. Part of Alaska is available at the 1/3 arc-second, 1 arc-second and 5 meter resolution. Efforts are continuing to have full coverage of the 5 meter elevation data over Alaska in the next couple of years.
"""

USGS_PROVIDER = Provider(
    name="USGS",
    roles=["producer", "processor", "host"],
    url="https://www.usgs.gov/core-science-systems/ngp/3dep")

USGS_FTP_SERVER = "rockyftp.cr.usgs.gov"
USGS_FTP_BASE = f"ftp://{USGS_FTP_SERVER}/vdelivery/Datasets/Staged/Elevation"
AWS_BUCKET = "prd-tnm"
AWS_PREFIX = "StagedProducts/Elevation"
AWS_BASE = f"https://{AWS_BUCKET}.s3.amazonaws.com/{AWS_PREFIX}"

DEFAULT_BASE = AWS_BASE