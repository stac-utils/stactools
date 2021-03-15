from __future__ import annotations
import datetime
from typing import Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from shapely.geometry import box, shape, mapping
from pystac import STAC_IO, Item, Asset, MediaType, Link

from stactools.core.projection import reproject_geom
from stactools.threedep.constants import THREEDEP_CRS, THREEDEP_EPSG, USGS_FTP_BASE
from stactools.threedep import utils


class Metadata:
    """3DEP file metadata."""
    @classmethod
    def from_href(cls, href: str) -> Metadata:
        """Creates a metadata from an href to the XML metadata file."""
        text = STAC_IO.read_text(href)
        element_tree = ElementTree.fromstring(text)
        return cls(element_tree)

    @classmethod
    def from_product_and_id(cls,
                            product: str,
                            id: str,
                            base_href=None) -> Metadata:
        """Creates a Metadata from a product and id.

        Optionally, pass base_href to use something other than the USGS FTP.
        """
        if base_href is None:
            base_href = USGS_FTP_BASE
        href = utils.path(product, id, base=base_href, extension="xml")
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
        self.base_href = USGS_FTP_BASE

    def to_item(self) -> Item:
        """Creates a STAC Item from these metadata."""
        geometry = self.geometry()
        bbox = list(shape(geometry).bounds)
        item = Item(id=self.stac_id(),
                    geometry=self.geometry(),
                    bbox=bbox,
                    datetime=self.datetime(),
                    properties={})
        start_datetime = self.start_datetime()
        end_datetime = self.end_datetime()
        if start_datetime and end_datetime:
            item.common_metadata.start_datetime = start_datetime
            item.common_metadata.end_datetime = end_datetime
        item.common_metadata.gsd = self.gsd()
        item.links.append(self.derived_from_link())
        item.assets["data"] = self.data_asset()
        item.assets["metadata"] = self.metadata_asset()
        item.assets["thumbnail"] = self.thumbnail_asset()
        item.ext.enable("projection")
        item.ext.projection.apply(**self.projection_extension_dict())
        return item

    def stac_id(self) -> str:
        """Returns the STAC ID of this metadata.

        This is the id plus the product, e.g. if the filename of the tif is
        "USGS_1_n40w105.tif", then the STAC id is "n40w105-1".
        """
        return "{}-{}".format(self.id, self.product)

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

    def datetime(self) -> Union[datetime.datetime, None]:
        """Returns the collection publication datetime."""
        if self.current == "publication date":
            return _format_date(self.pubdate)
        else:
            raise NotImplementedError

    def start_datetime(self) -> Union[datetime.datetime, None]:
        """Returns the start datetime for this record.

        This can be a while ago, since the national elevation dataset was
        originally derived from direct survey data.
        """
        return _format_date(self.begdate)

    def end_datetime(self) -> Union[datetime.datetime, None]:
        """Returns the end datetime for this record."""
        return _format_date(self.enddate, end_of_year=True)

    def gsd(self) -> float:
        """Returns the nominal ground sample distance from these metadata."""
        if self.product == "1":
            return 30
        elif self.product == "13":
            return 10
        else:
            raise NotImplementedError

    def data_asset(self) -> Asset:
        """Returns the data asset (aka the tiff file)."""
        return Asset(href=self._asset_href_with_extension("tif"),
                     title=self.title,
                     description=self.description,
                     media_type=MediaType.COG,
                     roles=["data"])

    def metadata_asset(self) -> Asset:
        """Returns the data asset (aka the tiff file)."""
        return Asset(href=self._asset_href_with_extension("xml"),
                     media_type=MediaType.XML,
                     roles=["metadata"])

    def thumbnail_asset(self) -> Asset:
        """Returns the numbnail asset."""
        return Asset(href=self._asset_href_with_extension("jpg"),
                     media_type=MediaType.JPEG,
                     roles=["thumbnail"])

    def derived_from_link(self) -> Link:
        """Returns the derived from link for this file."""
        return Link("derived_from", self._asset_href_with_extension("xml"))

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
        bbox = [
            float(self.minx),
            float(self.miny),
            float(self.maxx),
            float(self.maxy)
        ]
        centroid = {
            "lon": (bbox[0] + bbox[2]) / 2.0,
            "lat": (bbox[1] + bbox[3]) / 2.0,
        }
        geometry = mapping(box(*bbox))
        return {
            "epsg": THREEDEP_EPSG,
            "shape": shape,
            "transform": transform,
            "bbox": bbox,
            "centroid": centroid,
            "geometry": geometry,
        }

    def _asset_href_with_extension(self, extension: str) -> str:
        return utils.path(self.product,
                          self.id,
                          extension=extension,
                          base=self.base_href)


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
