import datetime

import dateutil.parser
import rasterio
from pystac import Item, Link, MediaType, STACError
from rasterio import RasterioIOError
from shapely.geometry import box, mapping, shape


def _parse_date(in_date: str) -> datetime.datetime:
    """
    Try to parse a date and return it as a datetime object with no timezone
    """
    parsed_date = dateutil.parser.parse(in_date)
    return parsed_date.replace(tzinfo=datetime.timezone.utc)


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
    acquired_date = _parse_date(
        f"{image['DATE_ACQUIRED']}T{image['SCENE_CENTER_TIME']}")
    created = _parse_date(proessing_record["DATE_PRODUCT_GENERATED"])

    item = Item(id=scene_id,
                geometry=geom,
                bbox=bounds,
                datetime=acquired_date,
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
    If `enable_proj` is true, the assets' geotiff files must be accessible.
    """
    # Clear hierarchical links
    item.set_parent(None)
    item.set_root(None)

    # Remove USGS extension and add back eo
    item.ext.enable("eo")

    # Add and update links
    if self_link:
        item.links.append(Link(rel="self", target=self_link))
    if source_link:
        item.links.append(
            Link(rel="derived_from",
                 target=source_link,
                 media_type="application/json"))

    # Add some common fields
    item.common_metadata.constellation = "Landsat"

    if not item.properties.get("eo:instrument"):
        raise STACError("eo:instrument missing among the properties")

    # Test if eo:instrument come as str or list
    if isinstance(item.properties["eo:instrument"], str):
        item.common_metadata.instruments = [
            i.lower() for i in item.properties.pop("eo:instrument").split("_")
        ]
    elif isinstance(item.properties["eo:instrument"], list):
        item.common_metadata.instruments = [
            i.lower() for i in item.properties.pop("eo:instrument")
        ]
    else:
        raise STACError(
            f'eo:instrument type {type(item.properties["eo:instrument"])} not supported'
        )

    # Handle view extension
    item.ext.enable("view")
    if (item.properties.get("eo:off_nadir")
            or item.properties.get("eo:off_nadir") == 0):
        item.ext.view.off_nadir = item.properties.pop("eo:off_nadir")
    elif (item.properties.get("view:off_nadir")
          or item.properties.get("view:off_nadir") == 0):
        item.ext.view.off_nadir = item.properties.pop("view:off_nadir")
    else:
        STACError("eo:off_nadir or view:off_nadir is a required property")

    if enable_proj:
        # Enabled projection
        item.ext.enable("projection")

        obtained_shape = None
        obtained_transform = None
        crs = None
        for asset in item.assets.values():
            if "geotiff" in asset.media_type:
                # retrieve shape, transform and crs from the first geotiff file among the assets
                if not obtained_shape:
                    try:
                        with rasterio.open(asset.href) as opened_asset:
                            obtained_shape = opened_asset.shape
                            obtained_transform = opened_asset.transform
                            crs = opened_asset.crs.to_epsg()
                            # Check to ensure that all information is present
                            if not obtained_shape or not obtained_transform or not crs:
                                raise STACError(
                                    f"Failed setting shape, transform and csr from {asset.href}"
                                )

                    except RasterioIOError as io_error:
                        raise STACError(
                            "Failed loading geotiff, so not handling proj fields"
                        ) from io_error

                item.ext.projection.set_transform(obtained_transform,
                                                  asset=asset)
                item.ext.projection.set_shape(obtained_shape, asset=asset)
                asset.media_type = MediaType.COG

        # Now we have the info, we can make the fields
        item.ext.projection.epsg = crs

    # Remove .TIF from asset names
    item.assets = {
        name.replace(".TIF", ""): asset
        for name, asset in item.assets.items()
    }

    return item


def stac_api_to_stac(uri: str) -> Item:
    """
    Takes in a URI and uses that to feed the STAC transform
    """

    return transform_stac_to_stac(item=Item.from_file(uri),
                                  source_link=uri,
                                  enable_proj=False)
