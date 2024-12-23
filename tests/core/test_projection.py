from shapely.geometry import Point

from stactools.core import projection


def test_no_precision() -> None:
    # This errors in stactools v0.5.0 because precision is None (needs to be an integer)
    projection.reproject_shape("EPSG:4326", "EPSG:4326", Point((0, 0)))
