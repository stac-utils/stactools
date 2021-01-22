import datetime

import dateutil
import rasterio
from pystac import Item, Link, MediaType
from rasterio import RasterioIOError
from shapely.geometry import box, mapping, shape


def _parse_date(in_date: str) -> datetime.datetime:
    """
    Try to parse a date and return it as a datetime object with no timezone
    """
    dt = dateutil.parser.parse(in_date)
    return dt.replace(tzinfo=datetime.timezone.utc)


def transform_mtl_to_stac(metadata: dict) -> Item:
    """
    Handle USGS MTL as a dict and return a STAC item.

    NOT IMPLEMENTED

    Issues include:
        - There's no reference to UTM Zone or any other CRS info in the MTL
        - There's no absolute file path or reference to a URI to find data.
    """
    LANDSAT_METADATA = metadata["LANDSAT_METADATA_FILE"]
    product = LANDSAT_METADATA["PRODUCT_CONTENTS"]
    projection = LANDSAT_METADATA["PROJECTION_ATTRIBUTES"]
    image = LANDSAT_METADATA["IMAGE_ATTRIBUTES"]
    proessing_record = LANDSAT_METADATA["LEVEL2_PROCESSING_RECORD"]

    scene_id = product["LANDSAT_PRODUCT_ID"]

    xmin, xmax = float(projection["CORNER_LL_LON_PRODUCT"]), float(
        projection["CORNER_UR_LON_PRODUCT"])
    ymin, ymax = float(projection["CORNER_LL_LAT_PRODUCT"]), float(
        projection["CORNER_UR_LAT_PRODUCT"])
    geom = mapping(box(xmin, ymin, xmax, ymax))
    bounds = shape(geom).bounds

    # Like: "2020-01-01" for date and  "23:08:52.6773140Z" for time
    dt = _parse_date(f"{image['DATE_ACQUIRED']}T{image['SCENE_CENTER_TIME']}")
    created = _parse_date(proessing_record["DATE_PRODUCT_GENERATED"])

    item = Item(id=scene_id,
                geometry=geom,
                bbox=bounds,
                datetime=dt,
                properties={})

    # Common metadata
    item.common_metadata.created = created
    item.common_metadata.platform = image["SPACECRAFT_ID"]
    item.common_metadata.instruments = [
        i.lower() for i in image["SENSOR_ID"].split("_")
    ]

    # TODO: implement these three extensions
    item.ext.enable("eo")
    item.ext.enable("view")
    item.ext.enable("projection")

    return item


def transform_stac_to_stac(item: Item,
                           enable_proj: bool = True,
                           self_link: str = None,
                           source_link: str = None) -> Item:
    """
    Handle a 0.7.0 item and convert it to a 1.0.0.beta2 item.
    """
    # Remove USGS extension and add back eo
    item.ext.enable("eo")

    # Add and update links
    item.links = []
    if self_link:
        item.links.append(Link(rel="self", target=self_link))
    if source_link:
        item.links.append(
            Link(rel="derived_from",
                 target=source_link,
                 media_type="application/json"))

    # Add some common fields
    item.common_metadata.constellation = "Landsat"
    item.common_metadata.instruments = [
        i.lower() for i in item.properties["eo:instrument"].split("_")
    ]
    del item.properties["eo:instrument"]

    # Handle view extension
    item.ext.enable("view")
    item.ext.view.off_nadir = item.properties["eo:off_nadir"]
    del item.properties["eo:off_nadir"]

    if enable_proj:
        try:
            # If we can load the blue band, use it to add proj information
            blue_asset = item.assets["SR_B2.TIF"]
            blue = rasterio.open(blue_asset.href)
            shape = [blue.height, blue.width]
            transform = blue.transform
            crs = blue.crs.to_epsg()

            # Now we have the info, we can make the fields
            item.ext.enable("projection")
            item.ext.projection.epsg = crs

            new_assets = {}

            for name, asset in item.assets.items():
                if asset.media_type == "image/vnd.stac.geotiff; cloud-optimized=true":
                    item.ext.projection.set_transform(transform, asset=asset)
                    item.ext.projection.set_shape(shape, asset=asset)
                    asset.media_type = MediaType.COG

        except RasterioIOError:
            print("Failed to load blue band, so not handling proj fields")

    # Remove .TIF from asset names
    new_assets = {}

    for name, asset in item.assets.items():
        new_name = name.replace(".TIF", "")
        new_assets[new_name] = asset
    item.assets = new_assets

    return item


def stac_api_to_stac(uri: str) -> dict:
    """
    Takes in a URI and uses that to feed the STAC transform
    """
    item = Item.from_file(uri)

    return transform_stac_to_stac(item, source_link=uri, enable_proj=False)
