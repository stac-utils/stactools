from typing import Any, Dict, List

import rasterio.features


def bounding_box(
    geom: Dict[str, Any]
) -> List[float]:
    """Extracts and returns the bounding box of a GeoJSON geometry.

    Args:
        geom (dict): A STAC Item, FeatureCollection, or GeoJSON geometry
    
    Returns:
        list: A list of float values containing the bounding box of the GeoJSON geometry in the 
        format [min X, min Y, max X, max Y] 
    """

    return list(rasterio.features.bounds(geom))