"""Generate convex hulls of valid raster data for use in STAC Item
geometries."""

import logging
import warnings
from itertools import groupby
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, TypeVar, Union

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

T = TypeVar("T", bound="RasterFootprint")


def densify_by_factor(
    point_list: List[Tuple[float, float]], factor: int
) -> List[Tuple[float, float]]:
    """Densifies the number of points in a list of points by a ``factor``. For
    example, a list of 5 points and a factor of 2 will result in 10 points (one
    new point between each original adjacent points).

    Derived from code found at
    https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw

    Args:
        point_list (List[Tuple[float, float]]): The list of points to be
            densified.
        factor (int): The factor by which to densify the points. A larger
            densification factor should be used when reprojection results in
            greater curvature from the original geometry.

    Returns:
        List[Tuple[float, float]]: A list of the densified points.
    """  # noqa: E501
    points: Any = np.asarray(point_list)
    densified_number = len(points) * factor
    existing_indices = np.arange(0, densified_number, factor)
    interp_indices = np.arange(existing_indices[-1])
    interp_x = np.interp(interp_indices, existing_indices, points[:, 0])
    interp_y = np.interp(interp_indices, existing_indices, points[:, 1])
    densified_points = [(x, y) for x, y in zip(interp_x, interp_y)]
    return densified_points


def densify_by_distance(
    point_list: List[Tuple[float, float]], distance: float
) -> List[Tuple[float, float]]:
    """Densifies the number of points in a list of points by inserting new
    points at intervals between each set of successive points. For example, if
    two successive points in the list are separated by 10 units and a
    ``distance`` of 2 is provided, 4 new points will be added between the two
    original points (one new point every 2 units of ``distance``).

    Derived from code found at
    https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw

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


def reproject_polygon(
    polygon: Polygon, crs: CRS, precision: Optional[int] = DEFAULT_PRECISION
) -> Polygon:
    """Projects a polygon to EPSG 4326 and rounds the projected vertex
    coordinates to ``precision``.

    Duplicate points caused by rounding are removed.

    Args:
        polygon (Polygon): The polygon to reproject.
        crs (CRS): The CRS of the input polygon.
        precision (int): The number of decimal places to include in the final
            polygon vertex coordinates.

    Returns:
        Polygon: Polygon in EPSG 4326.
    """
    polygon = shape(transform_geom(crs, "EPSG:4326", polygon, precision=precision))
    # Rounding to precision can produce duplicate coordinates, so we remove
    # them. Once once shapely>=2.0.0 is required, this can be replaced with
    # shapely.constructive.remove_repeated_points
    polygon = Polygon([k for k, _ in groupby(polygon.exterior.coords)])
    return polygon


class RasterFootprint:
    """An object for creating a convex hull polygon around all areas within an
    raster that have data values (i.e., they do not have the nodata value).
    This convex hull is termed the "footprint" of the raster data and is
    returned by the :meth:`footprint` method as a polygon in a GeoJSON
    dictionary for use as the geometry attribute of a STAC Item.

    Two important operations during this calculation are the densification of
    the footprint in the native CRS and simplification of the footprint after
    reprojection to EPSG 4326. If the initial low-vertex polygon in the native
    CRS is not densified, this can result in a reprojected polygon that does not
    accurately represent the data footprint. For example, a MODIS asset
    represented by a rectangular 5 point Polygon in a sinusoidal projection will
    reproject to a parallelogram in EPSG 4326, when it would be more accurately
    represented by a polygon with two parallel sides and two curved sides. The
    difference between these representations is greater the further away from
    the meridian and equator the asset is located.

    After reprojection to EPSG 4326, the footprint may have more points than
    desired. This can be simplified to a polygon with fewer points that maintain
    a maximum distance to the original geometry.

    Args:
        data_array (numpy.NDArray[Any]): The raster data used for the
            footprint calculation.
        crs (CRS): Coordinate reference system of the raster data.
        transform (Affine): Matrix defining the transformation from pixel to CRS
            coordinates.
        precision (int): The number of decimal places to include in the
            final footprint coordinates.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the footprint polygon before
            projection to EPSG 4326. A factor of 2 would double the density of
            points (placing one new point between each existing pair of points),
            a factor of 3 would place two points between each point, etc. Higher
            densities produce higher fidelity footprints in areas of high
            projection distortion. Mutually exclusive with
            ``densification_distance``.
        densification_distance (Optional[float]): The distance by which to
            increase point density within the footprint polygon before
            projection to EPSG 4326. If the distance is set to 2 and the segment
            length between two polygon vertices is 10, 4 new vertices would be
            created along the segment. Higher densities produce higher
            fidelity footprints in areas of high projection distortion.
            Mutually exclusive with ``densification_factor``.
        simplify_tolerance (Optional[float]): Distance, in degrees, within
            which all locations on the simplified polygon will be to the original
            polygon.
        no_data (Optional[Union[int, float]]): The nodata value in
            ``data_array``. If set to None, this will return a footprint
            including nodata values.
    """

    crs: CRS
    """Coordinate reference system of the raster data."""

    data_array: npt.NDArray[Any]
    """2D or 3D array of raster data."""

    densification_distance: Optional[float]
    """Optional distance for densifying polygon vertices before reprojection to
    EPSG 4326."""

    densification_factor: Optional[int]
    """Optional factor for densifying polygon vertices before reprojection to
    EPSG 4326."""

    no_data: Optional[Union[int, float]]
    """Optional value defining pixels to exclude from the footprint."""

    precision: int
    """Number of decimal places in the final footprint coordinates."""

    simplify_tolerance: Optional[float]
    """Optional maximum allowable error when simplifying the reprojected
    polygon."""

    transform: Affine
    """Transformation matrix from pixel to CRS coordinates."""

    def __init__(
        self,
        data_array: npt.NDArray[Any],
        crs: CRS,
        transform: Affine,
        *,
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
        no_data: Optional[Union[int, float]] = None,
    ) -> None:
        if data_array.ndim == 2:
            data_array = data_array[np.newaxis, :]
        self.data_array = data_array
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
        self.no_data = no_data

    def footprint(self) -> Optional[Dict[str, Any]]:
        """Produces the footprint surrounding data (not nodata) pixels in the
        source image. If the footprint is unable to be computed, None is
        returned.

        Returns:
            Optional[Dict[str, Any]]: A GeoJSON dictionary containing the
            footprint polygon.
        """
        mask = self.data_mask()
        polygon = self.data_extent(mask)
        if polygon is None:
            return None
        polygon = self.densify_polygon(polygon)
        polygon = self.reproject_polygon(polygon)
        polygon = self.simplify_polygon(polygon)
        return mapping(polygon)  # type: ignore

    def data_mask(self) -> npt.NDArray[np.uint8]:
        """Produces a mask of valid data in the source image. Nodata pixels
        values are set to 0, data pixels are set to 1.

        Returns:
            numpy.NDArray[numpy.uint8]: A 2D array containing 0s and 1s for
            nodata/data pixels.
        """
        assert self.data_array.ndim == 3
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
        """Produces the data footprint in the native CRS.

        Args:
            mask (numpy.NDArray[numpy.uint8]): A 2D array containing 0s and 1s for
                nodata/data pixels.

        Returns:
            Optional[Polygon]: A native CRS polygon of the convex hull of data
            pixels.
        """
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

        return polygon

    def densify_polygon(self, polygon: Polygon) -> Polygon:
        """Adds vertices to the footprint polygon in the native CRS using
        either ``self.densification_factor`` or
        ``self.densification_distance``.

        Args:
            polygon (Polygon): Footprint polygon in the native CRS.

        Returns:
            Polygon: Densified footprint polygon in the native CRS.
        """
        assert not (self.densification_factor and self.densification_distance)
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
        """Projects a polygon to EPSG 4326 and rounds the projected vertex
        coordinates to ``self.precision``.

        Duplicate points caused by rounding are removed.

        Args:
            polygon (Polygon): Footprint polygon in the native CRS.

        Returns:
            Polygon: Footprint polygon in EPSG 4326.
        """
        return reproject_polygon(polygon, self.crs, self.precision)

    def simplify_polygon(self, polygon: Polygon) -> Polygon:
        """Reduces the number of polygon vertices such that the simplified
        polygon shape is no further away than the original polygon vertices
        than ``self.simplify_tolerance``.

        Args:
            polygon (Polygon): Polygon to be simplified.

        Returns:
            Polygon: Reduced vertex polygon.
        """
        if self.simplify_tolerance is not None:
            return polygon.simplify(
                tolerance=self.simplify_tolerance, preserve_topology=False
            )
        return polygon

    @classmethod
    def from_href(
        cls: Type[T],
        href: str,
        *,
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
        no_data: Optional[Union[int, float]] = None,
        bands: List[int] = [1],
    ) -> T:
        """Produces a :class:`RasterFootprint` instance from an image href.

        The href can point to any file that is openable by rasterio.

        Args:
            href (str): The href of the image to process.
            precision (int): The number of decimal places to include in the
                final footprint coordinates.
            densification_factor (Optional[int]): The factor by which to
                increase point density within the footprint polygon before
                projection to EPSG 4326. A factor of 2 would double the density
                of points (placing one new point between each existing pair of
                points), a factor of 3 would place two points between each point,
                etc. Higher densities produce higher fidelity footprints in
                areas of high projection distortion. Mutually exclusive with
                ``densification_distance``.
            densification_distance (Optional[float]): The distance by which to
                increase point density within the footprint polygon before
                projection to EPSG 4326. If the distance is set to 2 and the
                segment length between two polygon vertices is 10, 4 new
                vertices would be created along the segment. Higher densities
                produce higher fidelity footprints in areas of high projection
                distortion.  Mutually exclusive with ``densification_factor``.
            simplify_tolerance (Optional[float]): Distance, in degrees, within
                which all locations on the simplified polygon will be to the
                original polygon.
            no_data (Optional[Union[int, float]]): Explicitly sets the nodata
                value if not in source image metadata. If set to None, this will
                return a footprint including nodata values.
            bands (List[int]): The bands to use to compute the footprint.
                Defaults to [1]. If an empty list is provided, the bands will be
                ORd together; e.g., for a pixel to be outside of the footprint,
                all bands must have nodata in that pixel.

        Returns:
            RasterFootprint: A :class:`RasterFootprint` instance.
        """
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
        cls: Type[T],
        reader: DatasetReader,
        *,
        precision: int = DEFAULT_PRECISION,
        densification_factor: Optional[int] = None,
        densification_distance: Optional[float] = None,
        simplify_tolerance: Optional[float] = None,
        no_data: Optional[Union[int, float]] = None,
        bands: List[int] = [1],
    ) -> T:
        """Produces a :class:`RasterFootprint` instance from a
        :class:`rasterio.io.DatasetReader`  object, i.e., an opened dataset
        object returned by a :func:`rasterio.open` call.

        Args:
            reader (DatasetReader): A rasterio dataset reader object for the
                image to process.
            precision (int): The number of decimal places to include in the
                final footprint coordinates.
            densification_factor (Optional[int]): The factor by which to
                increase point density within the footprint polygon before
                projection to EPSG 4326. A factor of 2 would double the density
                of points (placing one new point between each existing pair of
                points), a factor of 3 would place two points between each point,
                etc. Higher densities produce higher fidelity footprints in
                areas of high projection distortion. Mutually exclusive with
                ``densification_distance``.
            densification_distance (Optional[float]): The distance by which to
                increase point density within the footprint polygon before
                projection to EPSG 4326. If the distance is set to 2 and the
                segment length between two polygon vertices is 10, 4 new
                vertices would be created along the segment. Higher densities
                produce higher fidelity footprints in areas of high projection
                distortion.  Mutually exclusive with ``densification_factor``.
            simplify_tolerance (Optional[float]): Distance, in degrees, within
                which all locations on the simplified polygon will be to the
                original polygon.
            no_data (Optional[Union[int, float]]): Explicitly sets the nodata
                value if not in source image metadata. If set to None, this will
                return a footprint including nodata values.
            bands (List[int]): The bands to use to compute the footprint.
                Defaults to [1]. If an empty list is provided, the bands will be
                ORd together; e.g., for a pixel to be outside of the footprint,
                all bands must have nodata in that pixel.

        Returns:
            RasterFootprint: A :class:`RasterFootprint` instance.
        """
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

        band_data = []
        for index in bands:
            band_data.append(reader.read(index))

        return cls(
            data_array=np.asarray(band_data),
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
        """Accepts an Item and an optional list of asset names within that
        Item, and updates the geometry of that Item in-place with the data
        footprint derived from the first of the assets that exists in the Item.

        See :class:`RasterFootprint` for details on the data footprint
        calculation.

        Args:
            item (Item): The PySTAC Item to update.
            asset_names (List[str]): The names of the assets for which to attempt to
                extract footprints. The first successful footprint will be used. If
                the list is empty, all assets will be tried until one is successful.
            precision (int): The number of decimal places to include in the final
                footprint coordinates.
            densification_factor (Optional[int]): The factor by which to
                increase point density within the footprint polygon before
                projection to EPSG 4326. A factor of 2 would double the density
                of points (placing one new point between each existing pair of
                points), a factor of 3 would place two points between each point,
                etc. Higher densities produce higher fidelity footprints in
                areas of high projection distortion. Mutually exclusive with
                ``densification_distance``.
            densification_distance (Optional[float]): The distance by which to
                increase point density within the footprint polygon before
                projection to EPSG 4326. If the distance is set to 2 and the
                segment length between two polygon vertices is 10, 4 new
                vertices would be created along the segment. Higher densities
                produce higher fidelity footprints in areas of high projection
                distortion.  Mutually exclusive with ``densification_factor``.
            simplify_tolerance (Optional[float]): Distance, in degrees, within which
                all locations on the simplified polygon will be to the original
                polygon.
            no_data (Optional[Union[int, float]]): Explicitly sets the nodata value
                if not in source image metadata. If set to None, this will return
                a footprint including nodata values.
            bands (List[int]): The bands to use to compute the footprint.
                Defaults to [1]. If an empty list is provided, the bands will be ORd
                together; e.g., for a pixel to be outside of the footprint, all
                bands must have nodata in that pixel.
            skip_errors (bool): If False, raise an error for a missing href or
                footprint calculation failure.

        Returns:
            bool: True if the Item geometry was successfully updated, False if not.
        """
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
        """Accepts an Item and an optional list of asset names within that
        Item, and produces an iterator over the same asset names (if they
        exist) and dictionaries representing GeoJSON Polygons of the data
        footprints of the assets.

        See :class:`RasterFootprint` for details on the data footprint
        calculation.

        Args:
            item (Item): The PySTAC Item to update.
            asset_names (List[str]): The names of the assets for which to attempt to
                extract footprints. The first successful footprint will be used. If
                the list is empty, all assets will be tried until one is successful.
            precision (int): The number of decimal places to include in the final
                footprint coordinates.
            densification_factor (Optional[int]): The factor by which to
                increase point density within the footprint polygon before
                projection to EPSG 4326. A factor of 2 would double the density
                of points (placing one new point between each existing pair of
                points), a factor of 3 would place two points between each point,
                etc. Higher densities produce higher fidelity footprints in
                areas of high projection distortion. Mutually exclusive with
                ``densification_distance``.
            densification_distance (Optional[float]): The distance by which to
                increase point density within the footprint polygon before
                projection to EPSG 4326. If the distance is set to 2 and the
                segment length between two polygon vertices is 10, 4 new
                vertices would be created along the segment. Higher densities
                produce higher fidelity footprints in areas of high projection
                distortion.  Mutually exclusive with ``densification_factor``.
            simplify_tolerance (Optional[float]): Distance, in degrees, within which
                all locations on the simplified polygon will be to the original
                polygon.
            no_data (Optional[Union[int, float]]): Explicitly sets the nodata value
                if not in source image metadata. If set to None, this will return
                a footprint including nodata values.
            bands (List[int]): The bands to use to compute the footprint.
                Defaults to [1]. If an empty list is provided, the bands will be ORd
                together; e.g., for a pixel to be outside of the footprint, all
                bands must have nodata in that pixel.
            skip_errors (bool): If False, raise an error for a missing href or
                footprint calculation failure.

        Returns:
            Iterator[Tuple[str, Dict[str, Any]]]: Iterator of the asset name and
            dictionary representing a GeoJSON Polygon of the data footprint for
            each asset.
        """

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
    """DEPRECATED.

    .. deprecated:: 0.4.4
        Use :meth:`RasterFootprint.update_geometry_from_asset_footprint`
        instead.

    Accepts an Item and an optional list of asset names within that Item, and
    updates the geometry of that Item in-place with the data footprint derived
    from the first of the assets that exists in the Item.

    See :class:`RasterFootprint` for details on the data footprint
    calculation.

    Args:
        item (Item): The PySTAC Item to update.
        asset_names (List[str]): The names of the assets for which to attempt to
            extract footprints. The first successful footprint will be used. If
            the list is empty, all assets will be tried until one is successful.
        precision (int): The number of decimal places to include in the final
            footprint coordinates.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the polygon before projection to
            EPSG 4326. A factor of 2 would double the density of points (placing
            one new point between each existing pair of points), a factor of
            3 would place two points between each point, etc. Higher
            densities produce higher fidelity footprints in areas of high
            projection distortion.
        simplify_tolerance (Optional[float]): Distance, in degrees, within which
            all locations on the simplified polygon will be to the original
            polygon.
        no_data (Optional[Union[int, float]]): Explicitly sets the nodata value
            if not in source image metadata. If set to None, this will return
            a footprint including nodata values.
        bands (List[int]): The bands to use to compute the footprint.
            Defaults to [1]. If an empty list is provided, the bands will be ORd
            together; e.g., for a pixel to be outside of the footprint, all
            bands must have nodata in that pixel.
        skip_errors (bool): If False, raise an error for a missing href or
            footprint calculation failure.

    Returns:
        bool: True if the Item geometry was successfully updated, False if not.
    """
    warnings.warn(
        "update_geometry_from_asset_footprint() is deprecated, use "
        "RasterFootprint.update_geometry_from_asset_footprint() instead",
        DeprecationWarning,
    )
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
    """DEPRECATED.

    .. deprecated:: 0.4.4
        Use :meth:`RasterFootprint.data_footprints_for_data_assets`
        instead.

    Accepts an Item and an optional list of asset names within that Item, and
    produces an iterator over the same asset names (if they exist) and
    dictionaries representing GeoJSON Polygons of the data footprints of the
    assets.

    See :class:`RasterFootprint` for details on the data footprint
    calculation.

    Args:
        item (Item): The PySTAC Item to update.
        asset_names (List[str]): The names of the assets for which to attempt to
            extract footprints. The first successful footprint will be used. If
            the list is empty, all assets will be tried until one is successful.
        precision (int): The number of decimal places to include in the final
            footprint coordinates.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the polygon before projection to
            EPSG 4326. A factor of 2 would double the density of points (placing
            one new point between each existing pair of points), a factor of
            3 would place two points between each point, etc. Higher
            densities produce higher fidelity footprints in areas of high
            projection distortion.
        simplify_tolerance (Optional[float]): Distance, in degrees, within which
            all locations on the simplified polygon will be to the original
            polygon.
        no_data (Optional[Union[int, float]]): Explicitly sets the nodata value
            if not in source image metadata. If set to None, this will return
            a footprint including nodata values.
        bands (List[int]): The bands to use to compute the footprint.
            Defaults to [1]. If an empty list is provided, the bands will be ORd
            together; e.g., for a pixel to be outside of the footprint, all
            bands must have nodata in that pixel.
        skip_errors (bool): If False, raise an error for a missing href or
            footprint calculation failure.

    Returns:
        Iterator[Tuple[str, Dict[str, Any]]]: Iterator of the asset name and
        dictionary representing a GeoJSON Polygon of the data footprint for
        each asset.
    """
    warnings.warn(
        "data_footprints_for_data_assets() is deprecated, use "
        "RasterFootprint.data_footprints_for_data_assets() instead",
        DeprecationWarning,
    )
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
    """DEPRECATED.

    .. deprecated:: 0.4.4
        Call :meth:`~RasterFootprint.footprint` on a :class:`RasterFootprint`
        instance created with :meth:`RasterFootprint.from_href` instead.

    Produces a data footprint from the href of a raster file.

    See :class:`RasterFootprint` for details on the data footprint
    calculation.

    Args:
        href (str): The href of the image to process.
        precision (int): The number of decimal places to include in the final
            footprint coordinates.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the polygon before projection to
            EPSG 4326. A factor of 2 would double the density of points (placing
            one new point between each existing pair of points), a factor of
            3 would place two points between each point, etc. Higher
            densities produce higher fidelity footprints in areas of high
            projection distortion.
        simplify_tolerance (Optional[float]): Distance, in degrees, within which
            all locations on the simplified polygon will be to the original
            polygon.
        no_data (Optional[Union[int, float]]): Explicitly sets the nodata value
            if not in source image metadata. If set to None, this will return
            a footprint including nodata values.
        bands (List[int]): The bands to use to compute the footprint. Defaults
            to [1]. If an empty list is provided, the bands will be ORd
            together; e.g. for a pixel to be outside of the footprint, all bands
            must have nodata in that pixel.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing a GeoJSON Polygon of
        the data footprint of the raster data retrieved from the given ``href``.
    """
    warnings.warn(
        "data_footprint() is deprecated, use RasterFootprint.data_footprint() "
        "on a RasterFootprint instance created with "
        "RasterFootprint.from_href() instead",
        DeprecationWarning,
    )
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
    """Densifies the input polygon, reprojects it to EPSG 4326, and simplifies
    the resulting polygon.

    See :class:`RasterFootprint` for details on densification and
    simplification.

    Args:
        polygon (Polygon): The input polygon.
        crs (CRS): The CRS of the input polygon.
        densification_factor (Optional[int]): The factor by which to
            increase point density within the polygon before projection to
            EPSG 4326. A factor of 2 would double the density of points (placing
            one new point between each existing pair of points), a factor of
            3 would place two points between each point, etc. Higher
            densities produce higher fidelity footprints in areas of high
            projection distortion.
        precision (int): The number of decimal places to include in the final
            polygon vertex coordinates.
        simplify_tolerance (Optional[float]): Distance, in degrees, within which
            all locations on the simplified polygon will be to the original
            polygon.

    Returns:
        Polygon: The reprojected Polygon.
    """
    if densification_factor is not None:
        polygon = Polygon(
            densify_by_factor(polygon.exterior.coords, factor=densification_factor)
        )
    polygon = reproject_polygon(polygon, crs, precision)
    if simplify_tolerance is not None:
        polygon = polygon.simplify(
            tolerance=simplify_tolerance, preserve_topology=False
        )
    return polygon
