import logging
from typing import List

import numpy
import rasterio
from pystac import Item
from pystac.extensions.raster import (
    DataType,
    Histogram,
    RasterBand,
    RasterExtension,
    Statistics,
)
from pystac.utils import make_absolute_href

logger = logging.getLogger(__name__)

BINS = 256


def add_raster_to_item(item: Item) -> Item:
    """Adds the raster extension to an item.

    Args:
        item (Item): The PySTAC Item to extend.

    Returns:
        Item:
            Returns an updated Item.
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
        for i, index in enumerate(dataset.indexes):
            data = dataset.read(index, masked=True)
            band = RasterBand.create()
            band.nodata = dataset.nodatavals[i]
            band.spatial_resolution = dataset.transform[0]
            band.data_type = DataType(dataset.dtypes[i])
            minimum = float(numpy.min(data))
            maximum = float(numpy.max(data))
            band.statistics = Statistics.create(minimum=minimum, maximum=maximum)
            hist_data, _ = numpy.histogram(data, range=(minimum, maximum), bins=BINS)
            band.histogram = Histogram.create(
                BINS, minimum, maximum, hist_data.tolist()
            )
            bands.append(band)
    return bands
