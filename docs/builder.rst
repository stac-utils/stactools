Builders
========

A STAC Item can be thought of as one or more Assets with additional metadata,
some of which is derived from those assets. In many cases, creating an item from
geospatial assets is highly repeatable. The :py:mod:`stactools.core.builder`
module aims to abstract away many of the commonly-repeated operations required
to create items from assets.

Base class
----------

The base class, :py:class:`stactools.core.builder.Builder`, is pretty useless on
its own. It takes a dictionary of assets as its initializer, and wraps those
assets in an Item with a provided id and an auto-generated datetime::

    from stactools.core.builder import Builder
    from pystac import Asset

    builder = Builder()
    builder.add_asset("an-asset", Asset(href="a-file.dat"))
    item = builder.create_item(id="an-id")

    assert item.assets["an-asset"] == assets["an-asset"]

:py:class:`Builder` does have some smarts, however. For example, you can use the
builder to add ``file:checksum`` and ``file:size`` from the `file extension
<https://github.com/stac-extensions/file>`_, which require reading all of the
file's data (and is turned off by default)::

    from pystac.extensions.file import FileExtension

    builder = Builder()
    builder.add_asset("an-asset",
        Asset(href="a-file.dat"),
        include_file_extension=True)
    item = builder.create_item(id="an-id")
    file = FileExtension.ext(item.assets["an-asset"])
    assert file.size
    assert file.checksum

Subclasses of :py:class:`Builder` add more functionality.

Rasterio
--------

Many stactools packages are designed to work with raster assets that are
readable by `rasterio <https://rasterio.readthedocs.io/en/latest/>`_. The
:py:class:`stactools.core.builder.RasterioBuilder` class extends
:py:class:`Builder` to provide rasterio support::

    from stactools.core.builder import RasterioBuilder
    from pystac import Asset
    from pystac.extensions.projection import ProjectionExtension
    from pystac.extensions.raster import RasterExtension

    href = "https://github.com/stac-utils/stactools/raw/v0.3.0/tests/data-files/core/byte.tif"
    builder = RasterioBuilder()
    builder.add_rasterio_asset("an-asset", Asset(href=href))
    item = builder.create_item(id="an-id")

    assert item.geometry is not None
    ProjectionExtension.validate_has_extension(item, False)
    RasterExtension.validate_has_extension(item, False)

Single file rasterio
--------------------

Creating an item from a single rasterio-readable file is such a common use case,
:py:class:`stactools.core.builder.SingleFileRasterioBuilder` takes care of that
for you::

    from stactools.core.builder import SingleFileRasterioBuilder

    href = "https://github.com/stac-utils/stactools/raw/v0.3.0/tests/data-files/core/byte.tif"
    builder = SingleFileRasterioBuilder.from_href(href)
    item = builder.create_item()

    assert item.id == "byte"

You'll notice that you no longer need to pass ``id`` to ``create_item`` -- the
ID is deduced from the file name.

Custom subclasses
-----------------

Datasets can subclass ``Builder`` or any of its subclasses to provide their own
behavior.  Let's say there's a dataset that needs two files to create its items,
one rasterio-readable COG and a sidecar xml file. Its builder might look like this::

    import os.path

    from pystac import Asset, MediaType

    from stactools.core.builder import RasterioBuilder

    class FooBuilder(RasterioBuilder):

        @classmethod
        def from_hrefs(cls, cog_href: str, xml_href: str) -> "FooBuilder":
            cog_asset = Asset(href=cog_href, media_type=MediaType.COG)
            xml_asset = Asset(href=xml_href, media_type=MediaType.XML)
            builder = cls()
            builder.add_rasterio_asset("data", cog_asset)
            builder.add_asset("metadata", xml_asset)
            return builder

        def id(self) -> str:
            asset = self.get_asset("data")
            assert asset
            return os.path.splitext(os.path.basename(asset.href))[0]

        def create_item(self):
            item = super().create_item()

            # contrived example
            xml_asset = self.get_asset("metadata")
            assert xml_asset
            metadata = read_xml_metadata(xml_asset.href)
            for key, value in metadata.items():
                item.properties[key] = value

            return item
