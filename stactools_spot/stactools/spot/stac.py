import os
from datetime import datetime

import fiona
from pyproj import crs, Transformer
from pystac import (
    StacIO,
    Asset,
    Catalog,
    CatalogType,
    Collection,
    Item,
    MediaType,
    SpatialExtent,
    utils,
)
from shapely.geometry import box
from shapely.ops import transform as shapely_transform
from stactools.spot.geobase_ftp import GeobaseSpotFTP
from stactools.spot.stac_templates import build_catalog
from stactools.spot.utils import (
    bbox, 
    read_remote_stacs, 
    transform_geom, 
    write_remote_stacs
    )

StacIO.read_text = read_remote_stacs
StacIO.write_text = write_remote_stacs


def create_item(name, feature, collection):
    """
    name: SPOT ID
    feature: geojson feature
    collection: pySTAC collection object
    Create a STAC item for SPOT
    """

    item = Item(
        id=name,
        geometry=feature["geometry"],
        bbox=list(bbox(feature)),
        properties={},
        datetime=datetime.strptime(name[14:22], "%Y%m%d"),
        collection=collection,
    )
    return item


def build_items(index_geom, GeobaseSTAC):
    """
    index_geom: fiona readable file (ex, shapefile)
    Build the STAC items
    """
    with fiona.open(index_geom) as src:
        src_crs = crs.CRS(src.crs)
        dest_crs = crs.CRS("WGS84")

        extent = box(*src.bounds)

        transformer = Transformer.from_crs(src_crs, dest_crs)
        catalog_bbox = shapely_transform(transformer.transform, extent)

        # build spatial extent for collection
        ortho_collection = GeobaseSTAC.get_child("canada_spot_orthoimages")
        ortho_collection.extent.spatial = SpatialExtent([list(catalog_bbox.bounds)])

        geobase = GeobaseSpotFTP()

        count = 0
        for f in src:
            feature_out = f.copy()
            
            new_coords = transform_geom(transformer, f["geometry"]["coordinates"])
            feature_out["geometry"]["coordinates"] = new_coords

            name = feature_out["properties"]["NAME"]

            new_item = create_item(name, feature_out, ortho_collection)

            for f in geobase.list_contents(name):
                # Add data to the asset
                spot_file = Asset(href=f, title=None, media_type="application/zip")

                file_key = f[-13:-4]  # image type
                new_item.add_asset(file_key, spot_file)

            # Add the thumbnail asset
            new_item.add_asset(
                key="thumbnail",
                asset=Asset(
                    href=geobase.get_thumbnail(name),
                    title=None,
                    media_type=MediaType.JPEG,
                ),
            )

            ortho_collection.add_item(new_item)

            count += 1
            print(f"{count}... {new_item.id}")
    
    return GeobaseSTAC
