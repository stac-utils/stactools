import logging
from itertools import groupby
from typing import Any, Dict, Iterator, List, Optional, Tuple

import numpy as np
import numpy.typing as npt
import rasterio
import rasterio.features
from pystac import Item
from rasterio.crs import CRS
from rasterio.warp import transform_geom
from shapely.geometry import mapping, shape
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon

from stactools.core.projection import SINUSOIDAL_TILE_METERS, sinusoidal_grid_to_lonlat
from stactools.core.utils.round import recursive_round

logger = logging.getLogger(__name__)

# Roughly 1 centimeter in geodetic coordinates
DEFAULT_PRECISION = 7


class ItemRequired(Exception):
    """Item required to run the method."""


def _densify_by_factor(
    point_list: List[Tuple[float, float]], densification_factor: int
) -> List[Tuple[float, float]]:
    """
        Densifies the number of points in a list of points by a factor. For example, a list of 5 points
        and a densification_factor of 2 will result in 10 points (one new point between each original
        adjacent points.

        Derived from code found at
        https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw  # noqa

    Args:
        point_list (List[Tuple[float, float]]): The list of points.
        densification_factor (int): The factor by which to densify the points. A larger densification factor
            should be used when reprojection causes in greater curvature from the original geometry.

    Returns:
        List[Tuple[float, float]]: a list of the densified points
    """
    points: Any = np.asarray(point_list)
    densified_number = len(points) * densification_factor
    existing_indices = np.arange(0, densified_number, densification_factor)
    interp_indices = np.arange(existing_indices[-1])
    interp_x = np.interp(interp_indices, existing_indices, points[:, 0])  # noqa
    interp_y = np.interp(interp_indices, existing_indices, points[:, 1])  # noqa
    densified_points = [(x, y) for x, y in zip(interp_x, interp_y)]
    return densified_points


def _densify_by_distance(
    point_list: List[Tuple[float, float]], densification_length: float
) -> List[Tuple[float, float]]:
    """Densifies the number of points in a list of points by inserting new points
    at densification_length intervals between each set of points in the list. For
    example, if two successive points in the list are separated by 10 units and
    a densification_length of 2 is provided, 4 new points will be added
    between the two original points (one new point every 2 units of distance).

    Inspired from code found at
    https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw  # noqa

    Args:
        point_list (List[Tuple[float, float]]): The list of points to be
            densified.
        densification_length (float): The interval at which to insert additional
            points.

    Returns:
        List[Tuple[float, float]]: The list of densified points
    """
    points: Any = np.asarray(point_list)

    dxdy = points[1:, :] - points[:-1, :]
    segment_lengths = np.sqrt(np.sum(np.square(dxdy), axis=1))
    total_length = np.sum(segment_lengths)

    cum_segment_lengths = np.cumsum(segment_lengths)
    cum_segment_lengths = np.insert(cum_segment_lengths, 0, [0])
    cum_interp_lengths = np.arange(0, total_length, densification_length)
    cum_interp_lengths = np.append(cum_interp_lengths, [total_length])

    interp_x = np.interp(cum_interp_lengths, cum_segment_lengths, points[:, 0])
    interp_y = np.interp(cum_interp_lengths, cum_segment_lengths, points[:, 1])

    return [(x, y) for x, y in zip(interp_x, interp_y)]


class RasterFootprint:
    """Methods for updating Item geometry with the convex hull of valid raster data."""

    def __init__(
        self,
        *,
        asset_names: List[str] = [],
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        simplify_tolerance: Optional[float] = None,
        no_data: Optional[int] = None,
        bands: List[int] = [1],
    ) -> None:
        self.asset_names = asset_names
        self.precision = precision
        self.densification_factor = densification_factor
        self.simplify_tolerance = simplify_tolerance
        self.no_data = no_data
        self.bands = bands

    def update_geometry_from_asset_footprint(self, item: Item) -> bool:
        asset_name_and_extent = next(
            self.data_footprints_for_data_assets(item),
            None,
        )
        if asset_name_and_extent is not None:
            _, extent = asset_name_and_extent
            item.geometry = extent
            return True
        else:
            return False

    def data_footprints_for_data_assets(
        self, item: Item
    ) -> Iterator[Tuple[str, Dict[str, Any]]]:
        for name, asset in item.assets.items():
            if not self.asset_names or name in self.asset_names:
                href = asset.get_absolute_href()
                if href is None:
                    logger.error(
                        f"Could not determine extent for asset '{name}', missing href"
                    )
                else:
                    extent = self.data_footprint(href)
                    if extent:
                        yield name, extent
                    else:
                        logger.error(f"Could not determine extent for asset '{name}'")

    def data_footprint(self, href: str) -> Optional[Dict[str, Any]]:
        src = rasterio.open(href)

        # create datamask
        if self.no_data is None:
            self.no_data = src.nodata

        if not src.indexes:
            raise ValueError(
                "Raster footprint cannot be computed for an asset with no bands."
            )
        if not self.bands:
            self.bands = src.indexes

        if self.no_data is not None:
            data: npt.NDArray[np.uint8] = np.full(src.shape, 0, dtype=np.uint8)
            for index in self.bands:
                band_data = src.read(index, out_shape=src.shape)
                if np.isnan(self.no_data):
                    data[~np.isnan(band_data)] = 1
                else:
                    data[np.where(band_data != self.no_data)] = 1
        else:
            data = np.full(src.shape, 1, dtype=np.uint8)

        data_polygons = [
            shape(polygon_dict)
            for polygon_dict, region_value in rasterio.features.shapes(
                data, transform=src.transform
            )
            if region_value == 1
        ]

        if not data_polygons:
            return None
        elif len(data_polygons) == 1:
            polygon = data_polygons[0]
        else:
            polygon = MultiPolygon(data_polygons).convex_hull

        polygon = self.densify_reproject(polygon, src.crs)
        polygon = self.simplify(polygon)

        return mapping(polygon)  # type: ignore

    def densify_reproject(self, polygon: Polygon, crs: CRS) -> Polygon:
        if self.densification_factor is not None:
            polygon = Polygon(
                _densify_by_factor(polygon.exterior.coords, self.densification_factor)
            )

        polygon = shape(
            transform_geom(crs, "EPSG:4326", polygon, precision=self.precision)
        )

        return polygon

    def simplify(self, polygon: Polygon) -> Polygon:
        if self.simplify_tolerance is not None:
            polygon = polygon.simplify(
                tolerance=self.simplify_tolerance, preserve_topology=False
            ).simplify(0)

        # simplify does not remove duplicate sequential points, so do that
        return Polygon([k for k, _ in groupby(polygon.exterior.coords)])


class SinusoidalRasterFootprint(RasterFootprint):
    """Overrides the default RasterFootprint reprojection methods to generate
    Item geometries that play well at the edges of the sinusoidal projection
    used in MODIS and VIIRS data.
    """

    def __init__(
        self,
        horizontal_tile: int,
        vertical_tile: int,
        tile_dimension: int,
        *,
        asset_names: List[str] = [],
        precision: int = DEFAULT_PRECISION,
        simplify_tolerance: Optional[float] = None,
        no_data: Optional[int] = None,
        bands: List[int] = [1],
    ) -> None:
        super().__init__(
            asset_names=asset_names,
            precision=precision,
            simplify_tolerance=simplify_tolerance,
            no_data=no_data,
            bands=bands,
        )
        self.horizontal_tile = horizontal_tile
        self.vertical_tile = vertical_tile
        self.tile_dimension = tile_dimension

    def densify_reproject(self, polygon: Polygon, crs: CRS) -> Polygon:
        pixel_width = SINUSOIDAL_TILE_METERS / self.tile_dimension
        densified_points = _densify_by_distance(polygon.exterior.coords, pixel_width)
        lonlat_points = sinusoidal_grid_to_lonlat(densified_points)
        lonlat_points = [
            (lon, lat)
            for lon, lat in lonlat_points
            if lat >= -90 and lat <= 90 and lon >= -180 and lon <= 180
        ]
        return Polygon(recursive_round(lonlat_points, precision=self.precision))


def update_geometry_from_asset_footprint(
    item: Item,
    *,
    asset_names: List[str] = [],
    precision: int = DEFAULT_PRECISION,
    densification_factor: Optional[int] = None,
    simplify_tolerance: Optional[float] = None,
    no_data: Optional[int] = None,
    bands: List[int] = [1],
) -> bool:
    """
    Accepts an Item and an optional list of asset names within that item, and updates
    the geometry of that Item in-place with the data footprint derived from the first
    of the assets that exists in the Item.

    Two important operations during this calculation are the densification of the
    footprint in the native CRS and simplification of the footprint after reprojection.
    If the initial low-vertex polygon in the native CRS is not densified, this can result
    in a reprojected polygon that does not accurately represent the data footprint. For
    example, a MODIS asset represented by a rectangular 5 point Polygon in a sinusoidal
    projection will reproject to a parallelogram in EPSG 4326, when it would be more
    accurately represented by a polygon with two parallel sides and two curved sides.
    The difference between these representations is even greater the further away from
    the meridian and equator the asset is located.

    After reprojection to EPSG 4326, the footprint may have more points than desired.
    This can be simplified to a polygon with fewer points that maintain a minimum distance
    to the original geometry.

    Args:
        item (Item): The PySTAC Item to extend.
        asset_names (List[str]): The names of the assets for which to attempt to
            extract footprints. The first successful footprint will be used. If the
            list is empty, all assets will be tried until one is successful.
        precision (int): The number of decimal places to include in the coordinates for the
            reprojected geometry.
        densification_factor (Optional[int]): The factor by which to increase point density within
            the polygon.
            A factor of 2 would double the density of points (placing one new point between each
            existing pair
            of points), a factor of 3 would place two points between each point, etc.
        simplify_tolerance (Optional[float]): All points in the simplified object will be within
            the tolerance distance of the original geometry, in degrees.
        no_data(Optional[int]): explicitly set the no data value if not in image metadata
        bands (List[int]): The bands to use to compute the footprint. Defaults
            to [1]. If an empty list is provided, the bands will be ORd together;
            e.g. for a pixel to be outside of the footprint, all bands must have
            nodata in that pixel.

    Returns:
        bool: True if the extent was successfully updated, False if not
    """
    return RasterFootprint(
        asset_names=asset_names,
        precision=precision,
        densification_factor=densification_factor,
        simplify_tolerance=simplify_tolerance,
        no_data=no_data,
        bands=bands,
    ).update_geometry_from_asset_footprint(item)


def data_footprints_for_data_assets(
    item: Item,
    *,
    asset_names: List[str] = [],
    precision: int = DEFAULT_PRECISION,
    densification_factor: Optional[int] = None,
    simplify_tolerance: Optional[float] = None,
    no_data: Optional[int] = None,
    bands: List[int] = [1],
) -> Iterator[Tuple[str, Dict[str, Any]]]:
    """
    Accepts an Item and an optional list of asset names within that item, and
    produces an iterator over the same asset names (if they exist) and a
    dictionary representing a GeoJSON Polygon of the data footprint of the
    asset.  The data footprint is considered to be a convex hull around all
    areas within the raster that have data values (e.g., they do not have the
    "no data" value).

    See :py:meth:`update_geometry_from_asset_footprint` for more details about
    densification and simplification.

    Args:
        item (Item): The PySTAC Item to extend.
        asset_names (List[str]): The names of the assets for which to attempt to
            extract footprints. The first successful footprint will be used. If the
            list is empty, all assets will be tried until one is successful.
        precision (int): The number of decimal places to include in the coordinates for
            the reprojected geometry.
        densification_factor (Optional[int]): The factor by which to increase point density
            within the polygon. A factor of 2 would double the density of points (placing one
            new point between each existing pair of points), a factor of 3 would place two points
            between each point, etc.
        simplify_tolerance (Optional[float]): All points in the simplified object will be within
            the tolerance distance of the original geometry, in degrees.
        no_data(Optional[int]): explicitly set the no data value if not in image metadata
        bands (List[int]): The bands to use to compute the footprint. Defaults
            to [1]. If an empty list is provided, the bands will be ORd together;
            e.g. for a pixel to be outside of the footprint, all bands must have
            nodata in that pixel.
    Returns:
        Iterator[Tuple[str, Dict[str, Any]]]: Iterator of the data extent as a geojson dict
            for each asset.
    """
    return RasterFootprint(
        asset_names=asset_names,
        precision=precision,
        densification_factor=densification_factor,
        simplify_tolerance=simplify_tolerance,
        no_data=no_data,
        bands=bands,
    ).data_footprints_for_data_assets(item)


def data_footprint(
    href: str,
    *,
    precision: int = DEFAULT_PRECISION,
    densification_factor: Optional[int] = None,
    simplify_tolerance: Optional[float] = None,
    no_data: Optional[int] = None,
    bands: List[int] = [1],
) -> Optional[Dict[str, Any]]:
    """
    Produces a data footprint from the href of a raster file.

    See :py:meth:`update_geometry_from_asset_footprint` for more details about densification
    and simplification.

    Args:
        href (str): The href of the image to process.
        precision (int): The number of decimal places to include in the coordinates for the
            reprojected geometry.
        densification_factor (Optional[int]): The factor by which to increase point density
            within the polygon. A factor of 2 would double the density of points (placing one
            new point between each existing pair of points), a factor of 3 would place two points
            between each point, etc.
        simplify_tolerance (Optional[float]): All points in the simplified object will be within
            the tolerance distance of the original geometry, in degrees.
        no_data (Optional[int]): explicitly set the no data value if not in image metadata. If
            set to None, this will return the footprint including no data values.
        bands (List[int]): The bands to use to compute the footprint. Defaults
            to [1]. If an empty list is provided, the bands will be ORd together;
            e.g. for a pixel to be outside of the footprint, all bands must have
            nodata in that pixel.

    Returns:
        List[Tuple[float, float]]: a list of the densified points
    """
    return RasterFootprint(
        precision=precision,
        densification_factor=densification_factor,
        simplify_tolerance=simplify_tolerance,
        no_data=no_data,
        bands=bands,
    ).data_footprint(href)


def densify_reproject_simplify(
    polygon: Polygon,
    crs: CRS,
    *,
    densification_factor: Optional[int] = None,
    precision: int = DEFAULT_PRECISION,
    simplify_tolerance: Optional[float] = None,
) -> Polygon:
    """
    From the input Polygon, densifies the polygon, reprojects it to EPSG:4326, and then
    simplifies the resulting polygon.

    See :py:meth:`update_geometry_from_asset_footprint` for more details about densification
    and simplification.

    Args:
        polygon (Polygon): The input Polygon
        crs (CRS): The CRS of the input Polygon
        densification_factor (Optional[int]): The factor by which to increase point density
            within the polygon. A factor of 2 would double the density of points (placing one
            new point between each existing pair of points), a factor of 3 would place two points
            between each point, etc.
        precision (int): The number of decimal places to include in the coordinates for the
            reprojected geometry.
        simplify_tolerance (Optional[float]): All points in the simplified object will be within
            the tolerance distance of the original geometry, in degrees.

    Returns:
        Polygon: the reprojected Polygon
    """
    raster_footprint = RasterFootprint(
        precision=precision,
        densification_factor=densification_factor,
        simplify_tolerance=simplify_tolerance,
    )
    polygon = raster_footprint.densify_reproject(polygon, crs)
    polygon = raster_footprint.simplify(polygon)
    return polygon
