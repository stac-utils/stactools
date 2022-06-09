import logging
from typing import Any, Dict, Iterator, List, Optional, Tuple

import numpy
import rasterio
from pystac import Item
from pystac.utils import make_absolute_href
from rasterio import Affine
from rasterio.warp import transform_geom
from shapely.geometry import mapping, shape

logger = logging.getLogger(__name__)


def data_extents_for_data_assets(
    item: Item, asset_names: Optional[List[str]] = None, **kwargs: Any
) -> Iterator[Tuple[str, Dict[str, Any]]]:
    """

    Args:
        item (Item): The PySTAC Item to extend.
        asset_names (Optional[List[str]]): the names of the assets to extract extents for.

    Returns:
        Iterator[Tuple[str, Dict[str, Any]]]: Iterator of the data extent as a geojson dict
            for each asset.
    """
    for name, asset in item.assets.items():
        if (
            asset.roles
            and "data" in asset.roles
            and (asset_names is None or name in asset_names)
        ):
            href = make_absolute_href(asset.href, item.get_self_href())
            extent = data_extent(href, **kwargs)
            if extent:
                yield name, extent
            else:
                logger.error(f"Could not determine extent for asset '{name}'")


def data_extent(
    href: str,
    *,
    scale: int = 1,
    tolerance: Optional[float] = None,
    precision: int = 3,
    preserve_topology: bool = True,
) -> Optional[Dict[str, Any]]:
    src = rasterio.open(href)

    # generate datamask
    scaled_out_shape = (int(src.shape[0] / scale), int(src.shape[1] / scale))
    arr = src.read(indexes=[1], out_shape=scaled_out_shape)
    arr[numpy.where(arr != 0)] = 1

    shapes_transform = src.transform * Affine.scale(scale)

    for polygon_dict, region_value in rasterio.features.shapes(
        arr, transform=shapes_transform
    ):

        # Option 1
        # transform_geom only transforms the points in the geometry, so they need to be
        # densified first
        # possibly use densification code here:
        # https://github.com/pjhartzell/viirs
        # /blob/5622e9a986a1c9c75dbb071497b23facbbb4166c/src/stactools/viirs/metadata.py#L265
        geometry = shape(
            transform_geom(src.crs, "EPSG:4326", polygon_dict, precision=precision)
        )

        print(f">>> {geometry}")

        # Option 2
        # a transformer with an accuracy (meters) should densify and then reproject, but this throws
        #  pyproj.exceptions.ProjError: Error creating Transformer from CRS.
        # geometry = shape(transform(
        #     pyproj.Transformer.from_crs(
        #         pyproj.CRS(src.crs),
        #         pyproj.CRS("EPSG:4326"),
        #         # always_xy=True,
        #         accuracy=100000).transform,
        #     shape(polygon_dict)))
        #
        # print(f">>> {geometry}")

        if region_value == 1:
            if tolerance is not None:
                geometry = geometry.simplify(tolerance, preserve_topology)
            return mapping(geometry)  # type: ignore

    return None


def update_geometry_from_asset_extent(
    item: Item, asset_names: Optional[List[str]] = None, **kwargs: Any
) -> Optional[Item]:
    asset_name_and_extent = next(
        data_extents_for_data_assets(item, asset_names, **kwargs), None
    )
    if asset_name_and_extent is not None:
        _, extent = asset_name_and_extent
        item.geometry = extent
        return item
    else:
        return None
