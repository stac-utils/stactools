import datetime
import os.path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

import pyproj
import rasterio
import shapely.geometry
from pyproj.enums import WktVersion
from pystac import Asset, Item, MediaType
from pystac.extensions.file import FileExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import RasterBand, RasterExtension
from rasterio.crs import CRSError

import stactools.core.projection
import stactools.core.utils.convert
from stactools.core.io import FileInfo, ReadHrefModifier

EPSG = 4326
DEFAULT_INCLUDE_PROJECTION_EXTENSION = True
DEFAULT_INCLUDE_RASTER_EXTENSION = True
DEFAULT_INCLUDE_FILE_EXTENSION = False
Object = Dict[str, Any]


@dataclass
class AssetInfo:
    geometry: Optional[Object]
    projection: Optional[Object]
    raster: Optional[Object]


@dataclass
class ItemInfo:
    geometry: Optional[Object]
    projection: Optional[Object]
    asset_infos: Dict[str, AssetInfo]


class Builder:

    include_projection_extension: bool

    _assets: Dict[str, Asset]
    _projection_keys: Set[str]
    _raster_keys: Set[str]
    _file_keys: Set[str]

    def __init__(
        self,
        *,
        include_projection_extension: bool = DEFAULT_INCLUDE_PROJECTION_EXTENSION,
    ) -> None:
        """Creates a new builder with no assets."""
        self._assets = {}
        self._projection_keys = set()
        self._raster_keys = set()
        self._file_keys = set()
        self.include_projection_extension = include_projection_extension

    def get_asset(self, key: str) -> Optional[Asset]:
        """Gets an asset by key."""
        return self._assets.get(key)

    def add_asset(
        self,
        key: str,
        asset: Asset,
        *,
        include_projection_extension: bool = DEFAULT_INCLUDE_PROJECTION_EXTENSION,
        include_raster_extension: bool = DEFAULT_INCLUDE_RASTER_EXTENSION,
        include_file_extension: bool = DEFAULT_INCLUDE_FILE_EXTENSION,
    ) -> Optional[Asset]:
        """Adds an asset to this builder.

        Returns the old asset if this key already existed.
        """
        old_asset = self._assets.pop(key, None)
        self._assets[key] = asset
        if include_projection_extension:
            self._projection_keys.add(key)
        if include_raster_extension:
            self._raster_keys.add(key)
        if include_file_extension:
            self._file_keys.add(key)
        return old_asset

    def add_assets(self, assets: Dict[str, Asset]) -> Dict[str, Asset]:
        """Adds assets to this builder.

        Returns any old assets.
        """
        old_assets = dict()
        for key, asset in assets.items():
            old_asset = self.add_asset(key, asset)
            if old_asset:
                old_assets[key] = old_asset
        return old_assets

    def remove_asset(self, key: str) -> Optional[Asset]:
        """Removes and returns an asset."""
        return self._assets.pop(key, None)

    def create_item(self, id: Optional[str] = None) -> Item:
        """Creates a pystac Item using this builder's assets.

        Returns:
            Item: The Item created by this builder.
        """
        item_info = self.item_info()
        if item_info.geometry:
            bbox = self.bbox(item_info.geometry)
        else:
            bbox = None

        item = Item(
            id=id or self.id(),
            geometry=item_info.geometry,
            bbox=bbox,
            datetime=self.datetime(),
            properties={},
        )
        for key, asset in self._assets.items():
            item.add_asset(key, asset)

        if self.include_projection_extension and item_info.projection:
            projection = ProjectionExtension.ext(item, add_if_missing=True)
            projection.apply(**item_info.projection)

        for key, asset in self._assets.items():
            if key in self._file_keys:
                file = FileExtension.ext(asset, add_if_missing=True)
                file_info = FileInfo.read(asset.href)
                file.checksum = file_info.checksum
                file.size = file_info.size

            asset_info = item_info.asset_infos.get(key)
            if not asset_info:
                continue
            if (
                self.include_projection_extension
                and key in self._projection_keys
                and asset_info.projection
            ):
                ProjectionExtension.add_to(item)  # can't ext an asset
                asset.extra_fields.update(asset_info.projection)
            if key in self._raster_keys and asset_info.raster:
                raster = RasterExtension.ext(asset, add_if_missing=True)
                raster.apply(**asset_info.raster)

        return item

    def id(self) -> str:
        raise NotImplementedError

    def datetime(self) -> datetime.datetime:
        """Returns this item's datetime.

        Returns:
            datetime.datetime: The item's datetime, defaults to `datetime.datetime.now()`.
        """
        return datetime.datetime.now()

    def item_info(self) -> ItemInfo:
        """Returns the ItemInfo object for this builder.

        ItemInfo contains optional fields that will be included in the final
        item, and AssetInfo objects that will be added to this builder's assets.
        This method includes logic to consolidate identical projection
        information from AssetInfo objects up to the ItemInfo.

        Returns:
            ItemInfo: The item's information, e.g. its geometry and asset information.
        """
        asset_infos = dict()
        projections = []
        geometries = []
        for key in self._assets:
            asset_info = self.asset_info(key)
            if asset_info is None:
                continue
            if asset_info.projection:
                projections.append(asset_info.projection)
            if asset_info.geometry:
                geometries.append(asset_info.geometry)
            asset_infos[key] = asset_info

        if projections and all(
            projection == projections[0] for projection in projections
        ):
            projection = projections[0]
            for key in asset_infos:
                asset_infos[key].projection = None
        else:
            projection = None

        geometry = self.geometry(geometries)

        return ItemInfo(
            geometry=geometry, asset_infos=asset_infos, projection=projection
        )

    def asset_info(self, key: str) -> Optional[AssetInfo]:
        """Returns the asset information for the provided key.

        By default, returns None, as some assets may be a no-op. Subclasses
        should override the method to return rich information about assets.

        Args:
            key (str): The asset key

        Returns:
            Optional[AssetInfo]: Either None, or information about the asset.
        """
        return None

    def geometry(self, geometries: List[Object]) -> Optional[Object]:
        """Returns a single geometry from a list of geometries that will be used
        as the item's geometry.

        By default, will return:
        - None, if the input list is empty,
        - The single geometry if all geometries are identical,
        - Or raise a ValueError if all geometries are not identical.

        Subclasses should override this method if they can provide geometries
        from other sources, or if they have logic to handle multiple geometries
        (e.g. enveloping).

        Args:
            geometries (List[Dict[str, Any]]): The input geometries.

        Raises:
            ValueError: Raised if the length of the input list is more than one.

        Returns:
            Optional[Dict[str, Any]]: The item's geometry, or None.
        """
        if not geometries:
            return None
        elif all(geometry == geometries[0] for geometry in geometries):
            return geometries[0]
        else:
            raise ValueError("Cannot determine a unique geometry for this item")

    def bbox(self, geometry: Object) -> List[float]:
        """Returns the bounding box for the item's geometry.

        By default, just returns the geometry's bounds, but subclasses could
        have different behavior.

        Args:
            geometry (Dict[str, Any]): The item's geometry

        Returns:
            List[float]: The bounding box.
        """
        return list(shapely.geometry.shape(geometry).bounds)


class RasterioBuilder(Builder):
    """Builds an item using rasterio to read information from assets."""

    read_href_modifier: Optional[ReadHrefModifier]
    """An optional function to modify the rasterio hrefs before reading.

    The assets' hrefs will not be modified.
    """

    _rasterio_keys: Set[str]

    def __init__(self) -> None:
        """Creates a new rasterio builder with no assets."""
        super().__init__()
        self._rasterio_keys = set()
        self.read_href_modifier = None

    def add_rasterio_asset(
        self,
        key: str,
        asset: Asset,
        *,
        include_projection_extension: bool = DEFAULT_INCLUDE_PROJECTION_EXTENSION,
        include_raster_extension: bool = DEFAULT_INCLUDE_RASTER_EXTENSION,
        include_file_extension: bool = DEFAULT_INCLUDE_FILE_EXTENSION,
    ) -> Optional[Asset]:
        """Adds an asset that will be read by rasterio to get band and
        projection information."""
        self._rasterio_keys.add(key)
        return self.add_asset(
            key,
            asset,
            include_projection_extension=include_projection_extension,
            include_raster_extension=include_raster_extension,
            include_file_extension=include_file_extension,
        )

    def asset_info(self, key: str) -> Optional[AssetInfo]:
        """Returns an asset info for assets specified in `self.rasterio_keys`.

        Uses `read_asset_info_with_rasterio` to do the reading.
        """
        if key in self._rasterio_keys:
            asset = self.get_asset(key)
            assert asset
            return self.read_asset_info_with_rasterio(asset)
        else:
            return None

    def read_asset_info_with_rasterio(self, asset: Asset) -> AssetInfo:
        """Reads a given asset with rasterio, return the asset's information.

        The asset information will include projection and raster information.

        Args:
            asset (Asset): The pystac asset to be read.

        Returns:
            AssetInfo: The asset information.
        """
        projection = dict()
        raster = dict()
        href = asset.href
        if self.read_href_modifier:
            href = self.read_href_modifier(asset.href)
        with rasterio.open(href) as dataset:
            crs = dataset.crs
            projection["bbox"] = dataset.bounds
            projection["transform"] = list(dataset.transform)[0:6]
            projection["shape"] = dataset.shape
            bands = list()
            for dtype, nodata, scale, offset, units in zip(
                dataset.dtypes,
                dataset.nodatavals,
                dataset.scales,
                dataset.offsets,
                dataset.units,
            ):
                bands.append(
                    RasterBand.create(
                        data_type=dtype,
                        nodata=nodata,
                        scale=scale,
                        offset=offset,
                        unit=units,
                    )
                )
            raster["bands"] = bands
        projection["geometry"] = shapely.geometry.mapping(
            shapely.geometry.box(*projection["bbox"])
        )
        try:
            projection["epsg"] = crs.to_epsg()
        except CRSError:
            projection["epsg"] = None
        if projection["epsg"] is None:
            pyproj_crs = pyproj.CRS.from_wkt(crs.to_wkt())
            projection["wkt2"] = pyproj_crs.to_wkt(WktVersion.WKT2_2019)
        if projection["epsg"] == EPSG:
            geometry = projection["geometry"]
        else:
            geometry = stactools.core.projection.reproject_geom(
                crs, f"EPSG:{EPSG}", projection["geometry"], precision=6
            )
        return AssetInfo(geometry=geometry, projection=projection, raster=raster)


class SingleFileRasterioBuilder(RasterioBuilder):
    """Creates an item from a single file."""

    DEFAULT_KEY = "data"
    """The default key that will point to the single file."""

    _key: str

    def __init__(
        self,
        key: str,
        asset: Asset,
        *,
        include_projection_extension: bool = DEFAULT_INCLUDE_PROJECTION_EXTENSION,
        include_raster_extension: bool = DEFAULT_INCLUDE_RASTER_EXTENSION,
        include_file_extension: bool = DEFAULT_INCLUDE_FILE_EXTENSION,
    ):
        """Creates a new builder with the given asset and asset key."""
        super().__init__()
        self._key = key
        self.add_rasterio_asset(
            key,
            asset,
            include_file_extension=include_file_extension,
            include_raster_extension=include_raster_extension,
            include_projection_extension=include_projection_extension,
        )

    @classmethod
    def from_href(
        cls, href: str, key: str = DEFAULT_KEY
    ) -> "SingleFileRasterioBuilder":
        return cls(key, Asset(href, roles=["data"]))

    @property
    def asset(self) -> Asset:
        """Returns the asset for the single file.

        Returns:
            Asset: The single file asset.
        """
        return self._assets[self._key]

    def id(self) -> str:
        """Sets the id to the basename (w/o extension) of the single file.

        Args:
            assets (Assets): The assets for this builder (unused).

        Returns:
            str: The id for the item.
        """
        return os.path.splitext(os.path.basename(self.asset.href))[0]


class SingleCOGBuilder(SingleFileRasterioBuilder):
    """Creates an item from a single COG file."""

    @classmethod
    def from_href(
        cls,
        href: str,
        key: str = SingleFileRasterioBuilder.DEFAULT_KEY,
        *,
        include_projection_extension: bool = DEFAULT_INCLUDE_PROJECTION_EXTENSION,
        include_raster_extension: bool = DEFAULT_INCLUDE_RASTER_EXTENSION,
        include_file_extension: bool = DEFAULT_INCLUDE_FILE_EXTENSION,
    ) -> "SingleCOGBuilder":
        return cls(
            key,
            Asset(href, roles=["data"], media_type=MediaType.COG),
            include_projection_extension=include_projection_extension,
            include_raster_extension=include_raster_extension,
            include_file_extension=include_file_extension,
        )
