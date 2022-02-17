import logging
from typing import List

import numpy
from pystac import Item
from pystac.utils import make_absolute_href
from pystac.extensions.raster import (DataType, Histogram, RasterBand,
                                      RasterExtension, Statistics)
import rasterio

logger = logging.getLogger(__name__)

BINS = 256


def add_raster_to_item(item: Item) -> Item:
    """Adds raster extension values to an item.

    Args:
        item (Item): The PySTAC Item to extend.

    Returns:
        Item: Returns an updated Item.
            This operation mutates the Item.
    """
    RasterExtension.add_to(item)
    for asset in item.assets.values():
        if asset.roles and "data" in asset.roles:
            raster = RasterExtension.ext(asset)
            href = make_absolute_href(asset.href, item.get_self_href())
            bands = _read_bands(href)
            if bands:
                raster.apply(bands)
    return item


def _read_bands(href: str) -> List[RasterBand]:
    bands = []
    with rasterio.open(href) as dataset:
        for (i, index) in enumerate(dataset.indexes):
            data = dataset.read(index, masked=True)
            band = RasterBand.create()
            band.nodata = dataset.nodatavals[i]
            band.spatial_resolution = dataset.transform[0]
            band.data_type = DataType(dataset.dtypes[i])
            # These `type: ignore` comments are required until `numpy>=1.22.0`.
            # When the minimum numpy version reaches v1.22.0 (which requires us
            # to drop Python 3.7), then we can remove these `type: ignore`
            # comments and remove the `warn_unused_ignores = True` line from
            # `mypy.ini`.
            minimum = float(numpy.min(data))  # type: ignore
            maximum = float(numpy.max(data))  # type: ignore
            band.statistics = Statistics.create(minimum=minimum,
                                                maximum=maximum)
            hist_data, _ = numpy.histogram(  # type: ignore
                data, range=(minimum, maximum), bins=BINS)
            band.histogram = Histogram.create(BINS, minimum, maximum,
                                              hist_data.tolist())
            bands.append(band)
    return bands
