from typing import Optional, Dict

from pystac import Item, Asset, MediaType
from pystac.extensions.projection import ProjectionExtension

from stactools.core.io import ReadHrefModifier
from stactools.goes import Dataset


def create_item(href: str,
                read_href_modifier: Optional[ReadHrefModifier] = None,
                cog_directory: Optional[str] = None,
                tight_geometry: bool = True) -> Item:
    """Creates a pystac.Item from a GOES netcdf file."""
    if read_href_modifier:
        href = read_href_modifier(href)
    dataset = Dataset(href, tight_geometry=tight_geometry)
    if cog_directory:
        cogs = dataset.cogify(cog_directory)
    else:
        cogs = {}
    return create_item_from_dataset(dataset, cogs)


def create_item_from_dataset(dataset: Dataset,
                             cogs: Dict[str, str] = {}) -> Item:
    """Creates a pystac.Item from a GOES dataset.

    Optionally, add in the provided COGS as assets. The cogs should be a
    dictionary of variable name -> path.
    """
    item = Item(id=dataset.id,
                geometry=dataset.geometry,
                bbox=dataset.bbox,
                datetime=dataset.datetime,
                properties={})
    item.common_metadata.start_datetime = dataset.start_datetime
    item.common_metadata.end_datetime = dataset.end_datetime

    ProjectionExtension.add_to(item)
    projection = ProjectionExtension.ext(item)
    projection.epsg = None
    projection.wkt2 = dataset.projection_wkt2
    projection.shape = dataset.projection_shape
    projection.transform = dataset.projection_transform

    item.add_asset(
        "data",
        Asset(href=dataset.original_href,
              title=dataset.title,
              description=dataset.description,
              media_type="application/netcdf",
              roles=["data"]))

    for variable, path in cogs.items():
        item.add_asset(
            variable,
            Asset(href=path,
                  title=(f"{dataset.title} "
                         f"Cloud Optimized Geotiff ({variable})"),
                  media_type=MediaType.COG,
                  roles=["data"]))
    return item
