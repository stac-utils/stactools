from functools import reduce
from typing import Any, Dict, List, Protocol

import rasterio.features
from shapely import Geometry


def bounding_box(geom: Dict[str, Any]) -> List[float]:
    """Extracts and returns the bounding box of a GeoJSON geometry.

    Args:
        geom (dict): A GeoJSON Feature, GeoJSON FeatureCollection, GeoJSON geometry,
            STAC Item, or STAC ItemCollection.

    Returns:
        list: A list of float values containing the bounding box of the GeoJSON
        geometry in the format [min X, min Y, max X, max Y]
    """
    return list(rasterio.features.bounds(geom))


def mutual_intersection(geoms: List[Geometry]) -> Geometry:
    """Finds the mutual intersection of a set of geometries.

    Args:
        geoms (List[Geometry]): A non-empty list of geometries to intersect

    Returns:
        Geometry: The mutual intersection of all geometries
    """
    assert len(geoms) > 0, "Must provide non-empty list of geometries"

    return reduce(
        lambda current, to_intersect: current.intersection(to_intersect),
        geoms[1:],
        geoms[0],
    )


class GeoInterface(Protocol):
    """A simple protocol for things that have a ``__geo_interface__`` method.

    The ``__geo_interface__`` protocol is described `here
    <https://gist.github.com/sgillies/2217756>`_, and is used within `shapely
    <https://shapely.readthedocs.io/en/stable/manual.html>`_ to
    extract geometries from objects.
    """

    def __geo_interface__(self) -> Dict[str, Any]:
        ...
