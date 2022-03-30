from typing import Optional

from pystac import Item

from stactools.core.builder import SingleFileRasterioBuilder
from stactools.core.io import ReadHrefModifier


def item(href: str, read_href_modifier: Optional[ReadHrefModifier] = None) -> Item:
    """Creates a STAC Item from the asset at the provided href.

    The `read_href_modifer` argument can be used to modify the href for the
    rasterio read, e.g. if you need to sign a url.

    This function is intentionally minimal in its signature and capabilities. If
    you need to customize your Item, do so after creation.
    """
    builder = SingleFileRasterioBuilder.from_href(href)
    builder.read_href_modifier = read_href_modifier
    item = builder.create_item()
    item.validate()
    return item
