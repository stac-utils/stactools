import datetime
import os.path
from typing import List, Optional

import rasterio
import shapely.geometry
import stactools.core.projection
from pystac import Asset, Item
from pystac.extensions.projection import ProjectionExtension

from .io import ReadHrefModifier


def item(
    href: str,
    *,
    asset_key: str = "data",
    roles: List[str] = ["data"],
    read_href_modifier: Optional[ReadHrefModifier] = None,
) -> Item:
    """Creates a STAC Item from the asset at the provided href.

    The ``read_href_modifer`` argument can be used to modify the href for the
    rasterio read, e.g. if you need to sign a url.

    This function is intentionally minimal in its signature and capabilities. If
    you need to customize your Item, do so after creation.

    Args:
        href (str): The href of the asset that will be used to create the item.
        asset_key (str): The unique key of the asset
        roles (List[str]): The semantic roles of the asset
        read_href_modifier (Optional[ReadHrefModifier]):
            An optional callable that will be used to modify the href before reading.

    Returns:
        pystac.Item: A PySTAC Item.
    """
    id = os.path.splitext(os.path.basename(href))[0]
    if read_href_modifier:
        modified_href = read_href_modifier(href)
    else:
        modified_href = href
    with rasterio.open(modified_href) as dataset:
        crs = dataset.crs
        proj_bbox = dataset.bounds
        proj_transform = list(dataset.transform)[0:6]
        proj_shape = dataset.shape
    geom = stactools.core.projection.reproject_shape(
        crs, "EPSG:4326", shapely.geometry.box(*proj_bbox), precision=6
    )
    bbox = list(geom.bounds)
    geojson = shapely.geometry.mapping(geom)
    item = Item(
        id=id,
        geometry=geojson,
        bbox=bbox,
        datetime=datetime.datetime.now(),
        properties={},
    )

    projection = ProjectionExtension.ext(item, add_if_missing=True)
    epsg = crs.to_epsg()
    if epsg:
        projection.epsg = epsg
    else:
        projection.wkt2 = crs.to_wkt("WKT2")
    projection.transform = proj_transform
    projection.shape = proj_shape

    item.add_asset(asset_key, Asset(href=href, roles=roles))

    return item
