import logging

from osgeo import gdal
from pystac import Item
from pystac.utils import make_absolute_href
from pystac.extensions.raster import (DataType, Histogram, RasterBand,
                                      RasterExtension, Statistics)

logger = logging.getLogger(__name__)

NUM_BUCKETS = 256


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
            bands = []
            href = make_absolute_href(asset.href, item.get_self_href())
            dataset = gdal.Open(href, gdal.GA_ReadOnly)
            for nband in range(dataset.RasterCount):
                gdal_band = dataset.GetRasterBand(nband + 1)
                band = RasterBand.create()
                band.nodata = gdal_band.GetNoDataValue()
                band.spatial_resolution = dataset.GetGeoTransform()[1]
                band.data_type = DataType(
                    gdal.GetDataTypeName(gdal_band.DataType).lower())
                minimum = gdal_band.GetMinimum()
                maximum = gdal_band.GetMaximum()
                if not minimum or not max:
                    minimum, maximum = gdal_band.ComputeRasterMinMax(True)
                band.statistics = Statistics.create(minimum=minimum,
                                                    maximum=maximum)
                hist_data = gdal_band.GetHistogram(minimum, maximum,
                                                   NUM_BUCKETS)
                band.histogram = Histogram.create(NUM_BUCKETS, minimum,
                                                  maximum, hist_data)
                bands.append(band)
            if bands:
                raster.apply(bands)
    return item
