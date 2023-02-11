"""Generate raster data footprints for use in STAC Item geometries."""

import logging
from itertools import groupby
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import numpy as np
import numpy.typing as npt
import rasterio
import rasterio.features
from pystac import Item
from rasterio import Affine, DatasetReader
from rasterio.crs import CRS
from rasterio.warp import transform_geom
from shapely.geometry import mapping, shape
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon

logger = logging.getLogger(__name__)

# Roughly 1 centimeter in geodetic coordinates
DEFAULT_PRECISION = 7


def densify_by_factor(
    point_list: List[Tuple[float, float]], factor: int
) -> List[Tuple[float, float]]:
    """
    Densifies the number of points in a list of points by a factor. For example,
    a list of 5 points and a factor of 2 will result in 10 points (one new point
    between each original adjacent points).

    Derived from code found at
    https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw  # noqa

    Args:
        point_list (List[Tuple[float, float]]): The list of points to be
            densified.
        factor (int): The factor by which to densify the points. A larger
            densification factor should be used when reprojection results in
            greater curvature from the original geometry.

    Returns:
        List[Tuple[float, float]]: A list of the densified points.
    """
    points: Any = np.asarray(point_list)
    densified_number = len(points) * factor
    existing_indices = np.arange(0, densified_number, factor)
    interp_indices = np.arange(existing_indices[-1])
    interp_x = np.interp(interp_indices, existing_indices, points[:, 0])  # noqa
    interp_y = np.interp(interp_indices, existing_indices, points[:, 1])  # noqa
    densified_points = [(x, y) for x, y in zip(interp_x, interp_y)]
    return densified_points


def densify_by_distance(
    point_list: List[Tuple[float, float]], distance: float
) -> List[Tuple[float, float]]:
    """
    Densifies the number of points in a list of points by inserting new
    points at intervals between each set of successive points. For example, if
    two successive points in the list are separated by 10 units and a distance
    of 2 is provided, 4 new points will be added between the two original points
    (one new point every 2 units of distance).

    Derived from code found at
    https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw # noqa

    Args:
        point_list (List[Tuple[float, float]]): The list of points to be
            densified.
        distance (float): The interval at which to insert additional points. A
            smaller densification distance should be used when reprojection
            results in greater curvature from the original geometry.

    Returns:
        List[Tuple[float, float]]: A list of the densified points.
    """
    points: Any = np.asarray(point_list)
    dxdy = points[1:, :] - points[:-1, :]
    segment_lengths = np.sqrt(np.sum(np.square(dxdy), axis=1))
    total_length = np.sum(segment_lengths)
    cum_segment_lengths = np.cumsum(segment_lengths)
    cum_segment_lengths = np.insert(cum_segment_lengths, 0, [0])
    cum_interp_lengths = np.arange(0, total_length, distance)
    cum_interp_lengths = np.append(cum_interp_lengths, [total_length])
    interp_x = np.interp(cum_interp_lengths, cum_segment_lengths, points[:, 0])
    interp_y = np.interp(cum_interp_lengths, cum_segment_lengths, points[:, 1])
    return [(x, y) for x, y in zip(interp_x, interp_y)]


class RasterFootprint:
    """An object for creating a convex hull polygon around pixels containing
    valid data (i.e., not "no data" pixels) for a single- or multi-band raster.
    """

    data_array: npt.NDArray[np.float_]
    """3D array of raster data."""

    crs: CRS
    """Coordinate reference system of the raster data."""

    transform: Affine
    """Transformation matrix from pixel to CRS coordinates."""

    no_data: Optional[Union[int, float]]
    """Optional value defining pixels to exclude from the footprint."""

    precision: int
    """Number of decimal places in the final footprint coordinates."""

    densification_factor: Optional[int]
    """Optional factor for densifying polygon vertices before reprojection."""

    densification_distance: Optional[float]
    """Optional distance for densifying polygon vertices before reprojection."""

    simplify_tolerance: Optional[float]
    """Optional maximum allowable error when simplifying the reprojected polygon."""

    def __init__(
        self,
        data_array: npt.NDArray[np.float_],
        crs: CRS,
        transform: Affine,
        *,
        no_data: Optional[Union[int, float]] = None,
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
    ) -> None:
        """Creates a new RasterFootprint instance ready for footprint creation.

        Args:
            data_array (npt.NDArray[np.float_]): 3D array of raster data.
            crs (CRS): Coordinate reference system of the raster data.
            transform (Affine): Transformation matrix from pixel to CRS
                coordinates.
            no_data (Optional[Union[int, float]]): Explicitly sets the no data
                value if not in source image metadata. If set to None, this will
                return the footprint including no data values.
            precision (int): The number of decimal places to include in the
                final footprint coordinates.
            densification_factor (Optional[int]): The factor by which to
                increase point density within the polygon before projection to
                WGS84. A factor of 2 would double the density of points (placing
                one new point between each existing pair of points), a factor of
                3 would place two points between each point, etc. Higher
                densities produce higher fidelity footprints in areas of high
                projection distortion. Mutually exclusive with
                densification_distance.
            densification_distance (Optional[float]): The distance by which to
                increase point density within the polygon before projection to
                WGS84. If the distance is set to 2 and the segment length
                between two polygon vertices is 10, 4 new vertices would be
                created along the segment. Higher densities produce higher
                fidelity footprints in areas of high projection distortion.
                Mutually exclusive with densification_factor
            simplify_tolerance (Optional[float]): All locations on the
                simplified polygon will be within simplify_tolerance distance of
                the original geometry, in degrees.
        """
        self.data_array = data_array
        self.no_data = no_data
        self.crs = crs
        self.transform = transform
        self.precision = precision

        if densification_factor is not None and densification_distance is not None:
            raise ValueError(
                "Only one of 'densification_factor' or 'densification_distance' "
                "can be specified."
            )
        self.densification_factor = densification_factor
        self.densification_distance = densification_distance

        self.simplify_tolerance = simplify_tolerance

    def footprint(self) -> Optional[Dict[str, Any]]:
        mask = self.data_mask()
        polygon = self.data_extent(mask)
        if polygon is None:
            return None
        polygon = self.densify_polygon(polygon)
        polygon = self.reproject_polygon(polygon)
        polygon = self.simplify_polygon(polygon)
        return mapping(polygon)  # type: ignore

    def data_mask(self) -> npt.NDArray[np.uint8]:
        shape = self.data_array.shape
        if self.no_data is not None:
            mask: npt.NDArray[np.uint8] = np.full(shape, 0, dtype=np.uint8)
            if np.isnan(self.no_data):
                mask[~np.isnan(self.data_array)] = 1
            else:
                mask[np.where(self.data_array != self.no_data)] = 1
            mask = np.sum(mask, axis=0, dtype=np.uint8)
            mask[mask > 0] = 1
        else:
            mask = np.full(shape, 1, dtype=np.uint8)
        return mask

    def data_extent(self, mask: npt.NDArray[np.uint8]) -> Optional[Polygon]:
        data_polygons = [
            shape(polygon_dict)
            for polygon_dict, region_value in rasterio.features.shapes(
                mask, transform=self.transform
            )
            if region_value == 1
        ]

        if not data_polygons:
            return None
        elif len(data_polygons) == 1:
            polygon = data_polygons[0]
        else:
            polygon = MultiPolygon(data_polygons).convex_hull

        return polygon  # type: ignore

    def densify_polygon(self, polygon: Polygon) -> Polygon:
        if self.densification_factor is not None:
            return Polygon(
                densify_by_factor(polygon.exterior.coords, self.densification_factor)
            )
        elif self.densification_distance is not None:
            return Polygon(
                densify_by_distance(
                    polygon.exterior.coords, self.densification_distance
                )
            )
        else:
            return polygon

    def reproject_polygon(self, polygon: Polygon) -> Polygon:
        polygon = shape(
            transform_geom(self.crs, "EPSG:4326", polygon, precision=self.precision)
        )
        # Rounding to precision can produce duplicate coordinates, so we remove
        # them. Once once shapely>=2.0.0 is supported, this can be replaced with
        # shapely.constructive.remove_repeated_points
        polygon = Polygon([k for k, _ in groupby(polygon.exterior.coords)])
        return polygon

    def simplify_polygon(self, polygon: Polygon) -> Polygon:
        if self.simplify_tolerance is not None:
            return polygon.simplify(
                tolerance=self.simplify_tolerance, preserve_topology=False
            )
        return polygon

    @classmethod
    def from_href(
        cls,
        href: str,
        *,
        no_data: Optional[Union[int, float]] = None,
        bands: List[int] = [1],
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
    ) -> "RasterFootprint":
        with rasterio.open(href) as source:
            return cls.from_rasterio_dataset_reader(
                reader=source,
                no_data=no_data,
                bands=bands,
                precision=precision,
                densification_factor=densification_factor,
                densification_distance=densification_distance,
                simplify_tolerance=simplify_tolerance,
            )

    @classmethod
    def from_rasterio_dataset_reader(
        cls,
        reader: DatasetReader,
        *,
        no_data: Optional[Union[int, float]] = None,
        bands: List[int] = [1],
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
    ) -> "RasterFootprint":
        if not reader.indexes:
            raise ValueError(
                "Raster footprint cannot be computed for an asset with no bands."
            )
        if len(set(reader.nodatavals)) != 1:
            raise ValueError("All raster bands must have the same 'nodata' value.")

        if not bands:
            bands = reader.indexes
        if no_data is None:
            no_data = reader.nodata

        band_list = []
        for index in bands:
            band_list.append(reader.read(index))

        return RasterFootprint(
            data_array=np.asarray(band_list),
            crs=reader.crs,
            transform=reader.transform,
            no_data=no_data,
            precision=precision,
            densification_factor=densification_factor,
            densification_distance=densification_distance,
            simplify_tolerance=simplify_tolerance,
        )

    @classmethod
    def update_geometry_from_asset_footprint(
        cls,
        item: Item,
        *,
        asset_names: List[str] = [],
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
        no_data: Optional[Union[int, float]] = None,
        bands: List[int] = [1],
        skip_errors: bool = True,
    ) -> bool:
        asset_name_and_extent = next(
            cls.data_footprints_for_data_assets(
                item,
                asset_names=asset_names,
                precision=precision,
                densification_factor=densification_factor,
                densification_distance=densification_distance,
                simplify_tolerance=simplify_tolerance,
                no_data=no_data,
                bands=bands,
                skip_errors=skip_errors,
            ),
            None,
        )
        if asset_name_and_extent is not None:
            _, extent = asset_name_and_extent
            item.geometry = extent
            return True
        else:
            return False

    @classmethod
    def data_footprints_for_data_assets(
        cls,
        item: Item,
        *,
        asset_names: List[str] = [],
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
        no_data: Optional[Union[int, float]] = None,
        bands: List[int] = [1],
        skip_errors: bool = True,
    ) -> Iterator[Tuple[str, Dict[str, Any]]]:
        def handle_error(message: str) -> None:
            if skip_errors:
                logger.error(message)
            else:
                raise Exception(message)

        for name, asset in item.assets.items():
            if not asset_names or name in asset_names:
                href = asset.get_absolute_href()
                if href is None:
                    handle_error(
                        f"Could not determine extent for asset '{name}', missing href"
                    )
                else:
                    extent = cls.from_href(
                        href=href,
                        no_data=no_data,
                        bands=bands,
                        precision=precision,
                        densification_factor=densification_factor,
                        densification_distance=densification_distance,
                        simplify_tolerance=simplify_tolerance,
                    ).footprint()
                    if extent:
                        yield name, extent
                    else:
                        handle_error(f"Could not determine extent for asset '{name}'")


def update_geometry_from_asset_footprint(
    item: Item,
    *,
    asset_names: List[str] = [],
    precision: int = DEFAULT_PRECISION,
    densification_factor: Optional[int] = None,
    simplify_tolerance: Optional[float] = None,
    no_data: Optional[Union[int, float]] = None,
    bands: List[int] = [1],
    skip_errors: bool = True,
) -> bool:
    """
    Accepts an Item and an optional list of asset names within that item, and
    updates the geometry of that Item in-place with the data footprint derived
    from the first of the assets that exists in the Item.

    Two important operations during this calculation are the densification of
    the footprint in the native CRS and simplification of the footprint after
    reprojection. If the initial low-vertex polygon in the native CRS is not
    densified, this can result in a reprojected polygon that does not accurately
    represent the data footprint. For example, a MODIS asset represented by a
    rectangular 5 point Polygon in a sinusoidal projection will reproject to a
    parallelogram in EPSG 4326, when it would be more accurately represented by
    a polygon with two parallel sides and two curved sides. The difference
    between these representations is even greater the further away from the
    meridian and equator the asset is located.

    After reprojection to EPSG 4326, the footprint may have more points than
    desired. This can be simplified to a polygon with fewer points that maintain
    a minimum distance to the original geometry.

    Args:
        item (Item): The PySTAC Item to update.
        asset_names (List[str]):
            The names of the assets for which to attempt to
            extract footprints. The first successful footprint will be used. If
            the list is empty, all assets will be tried until one is successful.
        precision (int): The number of decimal places to include in the final
            footprint coordinates.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the polygon before projection to
            WGS84. A factor of 2 would double the density of points (placing
            one new point between each existing pair of points), a factor of
            3 would place two points between each point, etc. Higher
            densities produce higher fidelity footprints in areas of high
            projection distortion.
        simplify_tolerance (Optional[float]): All locations on the simplified
            polygon will be within simplify_tolerance distance of the original
            geometry, in degrees.
        no_data (Optional[Union[int, float]]): Explicitly sets the no data value
            if not in source image metadata. If set to None, this will return
            the footprint including no data values.
        bands (List[int]): The bands to use to compute the footprint.
            Defaults to [1]. If an empty list is provided, the bands will be ORd
            together; e.g. for a pixel to be outside of the footprint, all bands
            must have nodata in that pixel.
        skip_errors (bool): Raise an error for missing hrefs and footprint
            geometry failures.

    Returns:
        bool: True if the Item geoemtry was successfully updated, False if not
    """
    return RasterFootprint.update_geometry_from_asset_footprint(
        item,
        asset_names=asset_names,
        precision=precision,
        densification_factor=densification_factor,
        simplify_tolerance=simplify_tolerance,
        no_data=no_data,
        bands=bands,
        skip_errors=skip_errors,
    )


def data_footprints_for_data_assets(
    item: Item,
    *,
    asset_names: List[str] = [],
    precision: int = DEFAULT_PRECISION,
    densification_factor: Optional[int] = None,
    simplify_tolerance: Optional[float] = None,
    no_data: Optional[Union[int, float]] = None,
    bands: List[int] = [1],
    skip_errors: bool = True,
) -> Iterator[Tuple[str, Dict[str, Any]]]:
    """
    Accepts an Item and an optional list of asset names within that item, and
    produces an iterator over the same asset names (if they exist) and a
    dictionary representing a GeoJSON Polygon of the data footprint of the
    asset. The data footprint is considered to be a convex hull around all
    areas within the raster that have data values (e.g., they do not have the
    "no data" value).

    See :py:meth:`update_geometry_from_asset_footprint` for more details about
    densification and simplification.

    Args:
        item (Item): The PySTAC Item to update.
        asset_names (List[str]): The names of the assets for which to attempt to
            extract footprints. The first successful footprint will be used. If
            the list is empty, all assets will be tried until one is successful.
        precision (int): The number of decimal places to include in the final
            footprint coordinates.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the polygon before projection to
            WGS84. A factor of 2 would double the density of points (placing
            one new point between each existing pair of points), a factor of
            3 would place two points between each point, etc. Higher
            densities produce higher fidelity footprints in areas of high
            projection distortion.
        simplify_tolerance (Optional[float]): All locations on the simplified
            polygon will be within simplify_tolerance distance of the original
            geometry, in degrees.
        no_data (Optional[Union[int, float]]): Explicitly sets the no data value
            if not in source image metadata.
        bands (List[int]): The bands to use to compute the footprint.
            Defaults to [1]. If an empty list is provided, the bands will be ORd
            together; e.g. for a pixel to be outside of the footprint, all bands
            must have nodata in that pixel.
        skip_errors (bool): Raise an error for missing hrefs and footprint
            geometry failures.

    Returns:
        Iterator[Tuple[str, Dict[str, Any]]]: Iterator of the asset name and
        dictionary representing a GeoJSON Polygon of the data footprint for
        each asset.
    """
    return RasterFootprint.data_footprints_for_data_assets(
        item,
        asset_names=asset_names,
        precision=precision,
        densification_factor=densification_factor,
        simplify_tolerance=simplify_tolerance,
        no_data=no_data,
        bands=bands,
        skip_errors=skip_errors,
    )


def data_footprint(
    href: str,
    *,
    precision: int = DEFAULT_PRECISION,
    densification_factor: Optional[int] = None,
    simplify_tolerance: Optional[float] = None,
    no_data: Optional[Union[int, float]] = None,
    bands: List[int] = [1],
) -> Optional[Dict[str, Any]]:
    """
    Produces a data footprint from the href of a raster file.

    See :py:meth:`update_geometry_from_asset_footprint` for more details about
    densification and simplification.

    Args:
        href (str): The href of the image to process.
        precision (int): The number of decimal places to include in the final
            footprint coordinates.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the polygon before projection to
            WGS84. A factor of 2 would double the density of points (placing
            one new point between each existing pair of points), a factor of
            3 would place two points between each point, etc. Higher
            densities produce higher fidelity footprints in areas of high
            projection distortion.
        simplify_tolerance (Optional[float]): All locations on the simplified
            polygon will be within simplify_tolerance distance of the original
            geometry, in degrees.
        no_data (Optional[Union[int, float]]): Explicitly sets the no data value
            if not in source image metadata. If set to None, this will return
            the footprint including no data values.
        bands (List[int]): The bands to use to compute the footprint.
            Defaults to [1]. If an empty list is provided, the bands will be ORd
            together; e.g. for a pixel to be outside of the footprint, all bands
            must have nodata in that pixel.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing a GeoJSON Polygon of
        the data footprint of the raster data retrieved from the passed href.
    """
    return RasterFootprint.from_href(
        href=href,
        no_data=no_data,
        bands=bands,
        precision=precision,
        densification_factor=densification_factor,
        simplify_tolerance=simplify_tolerance,
    ).footprint()


def densify_reproject_simplify(
    polygon: Polygon,
    crs: CRS,
    *,
    densification_factor: Optional[int] = None,
    precision: int = DEFAULT_PRECISION,
    simplify_tolerance: Optional[float] = None,
) -> Polygon:
    """
    From the input Polygon, densifies the polygon, reprojects it to EPSG:4326,
    and then simplifies the resulting polygon.

    See :py:meth:`update_geometry_from_asset_footprint` for more details about
    densification and simplification.

    Args:
        polygon (Polygon): The input Polygon.
        crs (CRS): The CRS of the input Polygon.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the polygon before projection to
            WGS84. A factor of 2 would double the density of points (placing
            one new point between each existing pair of points), a factor of
            3 would place two points between each point, etc. Higher
            densities produce higher fidelity footprints in areas of high
            projection distortion.
        precision (int): The number of decimal places to include in the final
            footprint coordinates.
        simplify_tolerance (Optional[float]): All locations on the simplified
            polygon will be within simplify_tolerance distance of the original
            geometry, in degrees.

    Returns:
        Polygon: The reprojected Polygon.
    """
    if densification_factor is not None:
        polygon = Polygon(
            densify_by_factor(polygon.exterior.coords, factor=densification_factor)
        )

    polygon = shape(transform_geom(crs, "EPSG:4326", polygon, precision=precision))
    polygon = Polygon([k for k, _ in groupby(polygon.exterior.coords)])

    if simplify_tolerance is not None:
        polygon = polygon.simplify(
            tolerance=simplify_tolerance, preserve_topology=False
        )

    return polygon
