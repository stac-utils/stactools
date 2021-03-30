# stactools.threedep

The 3D Elevation Program (3DEP), formerly known as the National Elevation Dataset (NED), is elevation data for the United States.
Because `3dep` isn't a valid Python package name, this package is named `stactools.threedep`.

## Usage

3DEP items are identified by two attributes: `product` and `id`.
`product` is a string that corresponds to the nominal resolution of the data.
Options are:

- "1": 1 arc-second DEMs
- "13" 1/3 arc-second DEMs

`id` is a lat-lon identifier, e.g. `n41w106`.

### Command line

To build a `pystac.Collection` directly from AWS into a directory named `usgs-3dep-stac`:

```bash
stac threedep create-collection usgs-3dep-stac
```

If you want to two-step the process, you can download the metadata first:

```bash
stac threedep download-metadata usgs-3dep-metadata
stac threedep create-collection usgs-3dep-stac --source usgs-3dep-metadata
```

### API

To create an item from AWS, use `stactools.threedep.stac.create_item`:

```python
from stactools.threedep import stac
item = stac.create_item_from_product_and_id("1", "n41w106")
```

You can also create an item directly from the href of a metadata XML file anyhwere:

```python
from stactools.threedep import stac
item = stac.create_item("ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Elevation/1/TIFF/n41w106/USGS_1_n41w106.xml")
```
