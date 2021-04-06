from typing import Optional

from pystac import Item
from shapely.geometry import shape

from stactools.core.io import ReadHrefModifier
from stactools.threedep.metadata import Metadata
from stactools.threedep.constants import DEFAULT_BASE


def create_item(href: str,
                read_href_modifier: Optional[ReadHrefModifier] = None,
                base: str = DEFAULT_BASE) -> Item:
    """Creates a STAC item from an href to an XML metadata file."""
    metadata = Metadata.from_href(href, read_href_modifier)
    return create_item_from_metadata(metadata, base)


def create_item_from_product_and_id(product: str,
                                    id: str,
                                    base: str = DEFAULT_BASE) -> Item:
    """Creates a STAC item from a product (e.g. "1") and an ID (e.g. "n41w106")."""
    metadata = Metadata.from_product_and_id(product, id)
    return create_item_from_metadata(metadata, base)


def create_item_from_metadata(metadata: Metadata, base: DEFAULT_BASE) -> Item:
    """Creates a STAC item from Metadata."""
    geometry = metadata.geometry
    bbox = list(shape(geometry).bounds)
    item = Item(id=metadata.stac_id,
                geometry=geometry,
                bbox=bbox,
                datetime=metadata.datetime,
                properties={})
    start_datetime = metadata.start_datetime
    end_datetime = metadata.end_datetime
    if start_datetime and end_datetime:
        item.common_metadata.start_datetime = start_datetime
        item.common_metadata.end_datetime = end_datetime
    item.common_metadata.gsd = metadata.gsd
    item.links.append(metadata.via_link(base))
    item.assets["data"] = metadata.data_asset(base)
    item.assets["metadata"] = metadata.metadata_asset(base)
    item.assets["thumbnail"] = metadata.thumbnail_asset(base)
    item.assets["gpkg"] = metadata.gpkg_asset(base)
    item.ext.enable("projection")
    item.ext.projection.apply(**metadata.projection_extension_dict)
    item.properties["threedep:region"] = metadata.region
    return item
