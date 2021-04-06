from __future__ import annotations
import datetime
from typing import Union, Optional
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from shapely.geometry import box, mapping
from pystac import Asset, MediaType, Link

from stactools.core import io
from stactools.core.io import ReadHrefModifier
from stactools.core.projection import reproject_geom
from stactools.threedep.constants import THREEDEP_CRS, THREEDEP_EPSG, DEFAULT_BASE
from stactools.threedep import utils


class Metadata:
    """3DEP file metadata."""
    @classmethod
    def from_href(
            cls,
            href: str,
            read_href_modifier: Optional[ReadHrefModifier] = None) -> Metadata:
        """Creates a metadata from an href to the XML metadata file."""
        text = io.read_text(href, read_href_modifier)
        element_tree = ElementTree.fromstring(text)
        return cls(element_tree)

    @classmethod
    def from_product_and_id(cls,
                            product: str,
                            id: str,
                            base: str = None) -> Metadata:
        """Creates a Metadata from a product and id."""
        if base is None:
            base = DEFAULT_BASE
        href = utils.path(product, id, extension="xml", base=base)
        return cls.from_href(href)

    def __init__(self, xml: Element):
        """Creates a new metadata object from XML metadata."""
        self.title = xml.findtext("./idinfo/citation/citeinfo/title")
        self.description = xml.findtext("./idinfo/descript/abstract")
        bounding = xml.find("./idinfo/spdom/bounding")
        self.minx = bounding.findtext("./westbc")
        self.miny = bounding.findtext("./southbc")
        self.maxx = bounding.findtext("./eastbc")
        self.maxy = bounding.findtext("./northbc")
        self.pubdate = xml.findtext("./idinfo/citation/citeinfo/pubdate")
        self.begdate = xml.findtext(
            "./idinfo/timeperd/timeinfo/rngdates/begdate")
        self.enddate = xml.findtext(
            "./idinfo/timeperd/timeinfo/rngdates/enddate")
        self.current = xml.findtext("./idinfo/timeperd/current")
        self.rowcount = xml.findtext("./spdoinfo/rastinfo/rowcount")
        self.colcount = xml.findtext("./spdoinfo/rastinfo/colcount")
        self.latres = xml.findtext("./spref/horizsys/geograph/latres")
        self.longres = xml.findtext("./spref/horizsys/geograph/longres")
        tiff_href = xml.findtext(
            "./distinfo/stdorder/digform/digtopt/onlinopt/computer/networka/networkr"
        )
        parts = tiff_href.split('/')[-4:]
        self.product = parts[0]
        self.id = parts[2]

    @property
    def stac_id(self) -> str:
        """Returns the STAC ID of this metadata.

        This is the id plus the product, e.g. if the filename of the tif is
        "USGS_1_n40w105.tif", then the STAC id is "n40w105-1".
        """
        return "{}-{}".format(self.id, self.product)

    @property
    def geometry(self) -> dict:
        """Returns this item's geometry in WGS84."""
        original_bbox = [
            float(self.minx),
            float(self.miny),
            float(self.maxx),
            float(self.maxy)
        ]
        return reproject_geom(THREEDEP_CRS, "EPSG:4326",
                              mapping(box(*original_bbox)))

    @property
    def datetime(self) -> Union[datetime.datetime, None]:
        """Returns the collection publication datetime."""
        if self.current == "publication date":
            return _format_date(self.pubdate)
        else:
            raise NotImplementedError

    @property
    def start_datetime(self) -> Union[datetime.datetime, None]:
        """Returns the start datetime for this record.

        This can be a while ago, since the national elevation dataset was
        originally derived from direct survey data.
        """
        return _format_date(self.begdate)

    @property
    def end_datetime(self) -> Union[datetime.datetime, None]:
        """Returns the end datetime for this record."""
        return _format_date(self.enddate, end_of_year=True)

    @property
    def gsd(self) -> float:
        """Returns the nominal ground sample distance from these metadata."""
        if self.product == "1":
            return 30
        elif self.product == "13":
            return 10
        else:
            raise NotImplementedError

    def data_asset(self, base: str = DEFAULT_BASE) -> Asset:
        """Returns the data asset (aka the tiff file)."""
        return Asset(href=self._asset_href_with_extension(base, "tif"),
                     title=self.title,
                     description=self.description,
                     media_type=MediaType.COG,
                     roles=["data"])

    def metadata_asset(self, base: str = DEFAULT_BASE) -> Asset:
        """Returns the data asset (aka the tiff file)."""
        return Asset(href=self._asset_href_with_extension(base, "xml"),
                     media_type=MediaType.XML,
                     roles=["metadata"])

    def thumbnail_asset(self, base: str = DEFAULT_BASE) -> Asset:
        """Returns the thumbnail asset."""
        return Asset(href=self._asset_href_with_extension(base, "jpg"),
                     media_type=MediaType.JPEG,
                     roles=["thumbnail"])

    def gpkg_asset(self, base: str = DEFAULT_BASE) -> Asset:
        """Returns the geopackage asset."""
        return Asset(href=self._asset_href_with_extension(base,
                                                          "gpkg",
                                                          id_only=True),
                     media_type=MediaType.GEOPACKAGE,
                     roles=["metadata"])

    def via_link(self, base: str = DEFAULT_BASE) -> Link:
        """Returns the via link for this file."""
        return Link("via", self._asset_href_with_extension(base, "xml"))

    @property
    def projection_extension_dict(self) -> dict:
        """Returns a dictionary of values to be applied to the projection extension."""
        shape = [int(self.rowcount), int(self.colcount)]
        transform = [
            float(self.longres),
            0.0,
            float(self.minx),
            0.0,
            -float(self.latres),
            float(self.maxy),
            0.0,
            0.0,
            1.0,
        ]
        return {
            "epsg": THREEDEP_EPSG,
            "shape": shape,
            "transform": transform,
        }

    @property
    def region(self) -> str:
        """Returns this objects 3dep "region".

        Region is defined as a 10x10 lat/lon box that nominally contains this item.
        E.g. for n41w106, the region would be n40w110. This is used mostly for
        creating subcatalogs for STACBrowser.
        """
        import math
        n_or_s = self.id[0]
        lat = float(self.id[1:3])
        if n_or_s == "s":
            lat = -lat
        lat = math.floor(lat / 10) * 10
        e_or_w = self.id[3]
        lon = float(self.id[4:])
        if e_or_w == "w":
            lon = -lon
        lon = math.floor(lon / 10) * 10
        return f"{n_or_s}{abs(lat)}{e_or_w}{abs(lon)}"

    def _asset_href_with_extension(self,
                                   base: str,
                                   extension: str,
                                   id_only: bool = False) -> str:
        if base is None:
            base = DEFAULT_BASE
        return utils.path(self.product,
                          self.id,
                          base=base,
                          extension=extension,
                          id_only=id_only)


def _format_date(date: str,
                 end_of_year: bool = False) -> Union[datetime.datetime, None]:
    if len(date) == 4:
        year = int(date)
        if end_of_year:
            month = 12
            day = 31
        else:
            month = 1
            day = 1
        if year < 1800 or year > datetime.date.today().year:
            return None  # There's some bad metadata in the USGS records
        else:
            return datetime.datetime(year,
                                     month,
                                     day,
                                     0,
                                     0,
                                     0,
                                     tzinfo=datetime.timezone.utc)
    elif len(date) == 8:
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])
        return datetime.datetime(year,
                                 month,
                                 day,
                                 0,
                                 0,
                                 0,
                                 tzinfo=datetime.timezone.utc)
    else:
        return None
