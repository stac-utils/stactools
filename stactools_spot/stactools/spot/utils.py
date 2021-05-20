import json
import urllib.request
from urllib.parse import urlparse

import boto3

from pystac import (
    StacIO,
    Catalog,
    Collection,
    Extent,
    Link,
    Provider,
    SpatialExtent,
    TemporalExtent,
)


def read_remote_stacs(uri):
    """
    Reads STACs from a remote location. To be used to set StacIO
    Defaults to local storage.
    """
    parsed = urlparse(uri)
    if parsed.scheme == "s3":
        bucket = parsed.netloc
        key = parsed.path[1:]
        s3 = boto3.resource("s3")
        obj = s3.Object(bucket, key)
        return json.loads(obj.get()["Body"].read().decode("utf-8"))
    if parsed.scheme in ["http", "https"]:
        with urllib.request.urlopen(uri) as url:
            stac = json.loads(url.read().decode())
            return stac
    else:
        return StacIO.default(uri)


def write_remote_stacs(uri, txt):
    """
    Writes STACs from a remote location. To be used to set STAC_IO
    Defaults to local storage.
    """
    parsed = urlparse(uri)
    if parsed.scheme == "s3":
        bucket = parsed.netloc
        key = parsed.path[1:]
        s3 = boto3.resource("s3")
        s3.Object(bucket, key).put(Body=txt)
    else:
        StacIO.default(uri, txt)


def bbox(f):
    x, y = zip(*list(explode(f["geometry"]["coordinates"])))
    return min(x), min(y), max(x), max(y)


def transform_geom(transformer, geom):
    """
    Transform the geometry of a given feature
    Allow multipolygons
    """
    new_coords = []
    for ring in geom:
        x2, y2 = transformer.transform(*zip(*ring))
        new_coords.append(list(zip(y2, x2)))

    return new_coords


def explode(coords):
    # from https://gis.stackexchange.com/questions/90553/fiona-get-each-feature-extent-bounds
    """Explode a GeoJSON geometry's coordinates object and yield coordinate tuples.
    As long as the input is conforming, the type of the geometry doesn't matter."""
    for e in coords:
        if isinstance(e, (float, int)):
            yield coords
            break
        else:
            for f in explode(e):
                yield f
