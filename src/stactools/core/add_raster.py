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


def add_raster_to_item(
    item: Item, statistics: bool = True, histogram: bool = True
) -> Item:
    """Adds the raster extension to an item.

    Args:
        item (Item): The PySTAC Item to extend.
        statistics (bool): Compute band statistics (min/max). Defaults to True
        histogram (bool): Compute band histogram. Defaults to True

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
            bands = _read_bands(href, statistics, histogram)
            if bands:
                raster.apply(bands)
    return item


def _read_bands(href: str, statistics: bool, histogram: bool) -> List[RasterBand]:
    bands = []
    with rasterio.open(href) as dataset:
        for i, index in enumerate(dataset.indexes):
            band = RasterBand.create()
            band.nodata = dataset.nodatavals[i]
            band.spatial_resolution = dataset.transform[0]
            band.data_type = DataType(dataset.dtypes[i])

            if statistics or histogram:
                data = dataset.read(index, masked=True)
                minimum = float(numpy.nanmin(data))
                maximum = float(numpy.nanmax(data))
            if statistics:
                band.statistics = Statistics.create(minimum=minimum, maximum=maximum)
            if histogram:
                # the entire array is masked, or all values are NAN.
                # won't be able to compute histogram and will return empty array.
                if numpy.isnan(minimum):
                    band.histogram = Histogram.create(0, minimum, maximum, [])
                else:
                    hist_data, _ = numpy.histogram(
                        data, range=(minimum, maximum), bins=BINS
                    )
                    band.histogram = Histogram.create(
                        BINS, minimum, maximum, hist_data.tolist()
                    )
            bands.append(band)
    return bands
