import dateutil
import os.path
from tempfile import TemporaryDirectory
from typing import Dict, Optional, List
from urllib.parse import urlparse

from h5py import File
import fsspec
from pyproj.crs import ProjectedCRS, GeographicCRS
from pyproj.crs.datum import CustomDatum, CustomEllipsoid
from pyproj.crs.coordinate_operation import GeostationarySatelliteConversion
from shapely.geometry import mapping, Polygon, box

from stactools.core.io import ReadHrefModifier
from stactools.core.projection import reproject_geom
from stactools.core.utils.convert import cogify

GOES_ELLIPSOID = CustomEllipsoid.from_name("GRS80")
BLOCKSIZE = 2**22


class Dataset:
    """A GOES dataset."""
    def __init__(self,
                 href: str,
                 tight_geometry: bool = True,
                 read_href_modifier: Optional[ReadHrefModifier] = None):
        """Creates a new dataset from a netcdf href."""
        # Projection stuff built with help from
        # https://github.com/OSGeo/gdal/blob/95e35bd1c40ec6ce33341ed6390cce955048067f/gdal/frmts/netcdf/netcdfdataset.cpp
        self.id = os.path.splitext(os.path.basename(href))[0]
        self.original_href = href
        if read_href_modifier:
            self.href = read_href_modifier(href)
        else:
            self.href = href
        self.variables = []
        with fsspec.open(self.href) as file:
            dataset = File(file)

            self.variables = [
                key for key in dataset.keys() if len(dataset[key].shape) == 2
            ]
            self.datetime = dateutil.parser.parse(
                dataset.attrs["date_created"])
            self.start_datetime = dateutil.parser.parse(
                dataset.attrs["time_coverage_start"])
            self.end_datetime = dateutil.parser.parse(
                dataset.attrs["time_coverage_end"])
            self.title = dataset.attrs["title"].decode("utf-8")
            self.description = dataset.attrs["summary"].decode("utf-8")
            projection = dataset["goes_imager_projection"]
            sweep_angle_axis = projection.attrs["sweep_angle_axis"].decode(
                "utf-8")
            satellite_height = projection.attrs["perspective_point_height"][
                0].item()
            latitude_natural_origin = projection.attrs[
                "latitude_of_projection_origin"][0].item()
            longitude_natural_origin = projection.attrs[
                "longitude_of_projection_origin"][0].item()
            extent = dataset["geospatial_lat_lon_extent"]
            xmin = extent.attrs["geospatial_westbound_longitude"][0].item()
            ymin = extent.attrs["geospatial_southbound_latitude"][0].item()
            xmax = extent.attrs["geospatial_eastbound_longitude"][0].item()
            ymax = extent.attrs["geospatial_northbound_latitude"][0].item()
            rowcount = len(dataset["x"][:])
            colcount = len(dataset["y"][:])
            x = dataset["x"][:].tolist()
            x_scale = dataset["x"].attrs["scale_factor"][0].item()
            x_offset = dataset["x"].attrs["add_offset"][0].item()
            y = dataset["y"][:].tolist()
            y_scale = dataset["y"].attrs["scale_factor"][0].item()
            y_offset = dataset["y"].attrs["add_offset"][0].item()

        # we let GRS80 and WGS84 be ~the same for these purposes, since we're
        # not looking for survey-level precision in these bounds
        self.bbox = [xmin, ymin, xmax, ymax]
        datum = CustomDatum(ellipsoid=GOES_ELLIPSOID)
        conversion = GeostationarySatelliteConversion(
            sweep_angle_axis, satellite_height, latitude_natural_origin,
            longitude_natural_origin)
        crs = ProjectedCRS(conversion=conversion,
                           geodetic_crs=GeographicCRS(datum=datum))
        self.projection_wkt2 = crs.to_wkt()
        self.projection_shape = [rowcount, colcount]
        x_bounds = [(x_scale * x + x_offset) * satellite_height
                    for x in [x[0], x[-1]]]
        y_bounds = [(y_scale * y + y_offset) * satellite_height
                    for y in [y[0], y[-1]]]
        xres = (x_bounds[1] - x_bounds[0]) / (rowcount - 1)
        yres = (y_bounds[1] - y_bounds[0]) / (colcount - 1)
        self.projection_transform = [
            xres, 0, x_bounds[0] - xres / 2, 0, yres, y_bounds[0] - yres / 2,
            0, 0, 1
        ]
        if tight_geometry:
            projection_geometry = Polygon([(x_bounds[0], y_bounds[0]),
                                           (x_bounds[0], y_bounds[1]),
                                           (x_bounds[1], y_bounds[1]),
                                           (x_bounds[1], y_bounds[0])])
            self.geometry = reproject_geom(crs, "EPSG:4326",
                                           mapping(projection_geometry))
        else:
            self.geometry = mapping(box(*self.bbox))

    def cogify(
        self,
        directory: str,
    ) -> Dict[str, str]:
        """Converts a GOES NetCDF file into two or more COGs in the provided output directory.

        Returns the cogs as a dict of variable name -> path. If there is just
        one variables and one data quality field, two cogs will be created.
        Compound datasets, e.g. MCMIP, will produce 2
        * n files, were n is the number of subdatasets.
        """
        if urlparse(self.href).scheme:
            with TemporaryDirectory() as temporary_directory:
                file_name = os.path.basename(self.original_href)
                local_path = os.path.join(temporary_directory, file_name)
                with fsspec.open(self.href) as source:
                    with fsspec.open(local_path, "wb") as target:
                        data = True
                        while data:
                            data = source.read(BLOCKSIZE)
                            target.write(data)
                return self._cogify(local_path, directory)
        else:
            return self._cogify(self.href, directory)

    def cog_file_names(self) -> List[str]:
        """Returns a list of all COG file names for this dataset."""
        return [self.cog_file_name(variable) for variable in self.variables]

    def cog_file_name(self, variable: str) -> str:
        """Returns the COG file name for the provided variable."""
        return f"{self.id}_{variable}.tif"

    def _cogify(self, path: str, directory: str) -> Dict[str, str]:
        cogs = {}
        for variable in self.variables:
            outfile = os.path.join(directory, self.cog_file_name(variable))
            cogify(self._gdal_path(path, variable), outfile)
            cogs[variable] = outfile
        return cogs

    def _gdal_path(self, path: str, variable: str) -> str:
        return f"netcdf:{path}:{variable}"
