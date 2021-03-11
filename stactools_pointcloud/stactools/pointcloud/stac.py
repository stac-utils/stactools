import datetime
import json
import os.path

from pdal import Pipeline
from pyproj import CRS
from pystac import Item, Asset
from pystac.extensions.pointcloud import PointcloudStatistic, PointcloudSchema
from shapely.geometry import shape, box, mapping

from stactools.core.projection import reproject_geom


def create_item(href,
                pdal_reader=None,
                compute_statistics=False,
                pointcloud_type="lidar",
                additional_providers=None):
    """Creates a STAC Item from a point cloud.

    Args:
        href (str): The href to the point cloud.
        pdal_reader (str): Override the default PDAL reader for this file extension.
        compute_statistics (bool): Set to true to compute statistics for the
        point cloud. Could take a while.
        pointcloud_type (str): The point cloud type, e.g. "lidar", "eopc",
        "radar", "sonar", or "other". Default is "lidar".

    Return:
        pystac.Item: A STAC Item representing this point cloud.
    """
    if pdal_reader:
        reader = {"type": pdal_reader, "filename": href}
    else:
        reader = href
    # This is the best way I can find right now to get header information
    # from PDAL-python without reading the whole file.
    pipeline = Pipeline(
        json.dumps([reader, {
            "type": "filters.head",
            "count": 0
        }]))
    pipeline.execute()
    metadata = json.loads(pipeline.get_metadata())["metadata"]
    try:
        reader_key = next(key for key in metadata.keys()
                          if key.startswith("readers"))
        if reader_key != "readers.las":
            # TODO support other formats
            raise Exception(
                "stactools currently only support las pointclouds, not {}".
                format(reader_key))
    except StopIteration:
        raise Exception("could not find reader key in pipeline metadata")
    metadata = metadata[reader_key]
    schema = pipeline.get_schema()["schema"]["dimensions"]

    id = os.path.splitext(os.path.basename(href))[0]
    encoding = os.path.splitext(href)[1][1:]
    spatialreference = CRS.from_string(metadata["spatialreference"])
    original_bbox = box(metadata["minx"], metadata["miny"], metadata["maxx"],
                        metadata["maxy"])
    geometry = reproject_geom(spatialreference,
                              "EPSG:4326",
                              mapping(original_bbox),
                              precision=6)
    bbox = list(shape(geometry).bounds)
    dt = datetime.datetime(
        metadata["creation_year"], 1,
        1) + datetime.timedelta(metadata["creation_doy"] - 1)

    item = Item(id=id,
                geometry=geometry,
                bbox=bbox,
                datetime=dt,
                properties={})

    if additional_providers is not None:
        item.common_metadata.providers.extend(additional_providers)

    item.add_asset(
        "pointcloud",
        Asset(href=href,
              media_type="application/octet-stream",
              roles=["data"],
              title="{} point cloud".format(encoding)))

    item.ext.enable("pointcloud")
    item.ext.pointcloud.count = metadata["count"]
    item.ext.pointcloud.type = pointcloud_type
    item.ext.pointcloud.encoding = encoding
    item.ext.pointcloud.schemas = [
        PointcloudSchema(schema) for schema in schema
    ]
    # TODO compute density.
    #
    # Do we just divide point clount by bounding box area? That's too low. But
    # computing a true boundary can be (usually is) expensive. Maybe if we run
    # stats we do a true density, but when we don't run stats we do the
    # quick-and-dirty? But then densities mean different things depending on
    # the processing history of the STAC file, which seems inconsistant.
    if compute_statistics:
        item.ext.pointcloud.statistics = _compute_statistics(reader)

    epsg = spatialreference.to_epsg()
    if epsg:
        item.ext.enable("projection")
        item.ext.projection.epsg = epsg
        item.ext.projection.wkt2 = spatialreference.to_wkt()
        item.ext.projection.bbox = list(original_bbox.bounds)

    return item


def _compute_statistics(reader):
    pipeline = Pipeline(json.dumps([reader, {"type": "filters.stats"}]))
    pipeline.execute()
    stats = json.loads(
        pipeline.get_metadata())["metadata"]["filters.stats"]["statistic"]
    stats = [PointcloudStatistic(stats) for stats in stats]
    return stats
