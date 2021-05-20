# stactools spot

A subpackage of stactools for working with [SPOT](https://open.canada.ca/data/en/dataset/d799c202-603d-4e5c-b1eb-d058803f80f9) data.

This subpackage converts the [Geobase Index shapefile](http://ftp.maps.canada.ca/pub/nrcan_rncan/image/spot/geobase_orthoimages/index/GeoBase_Orthoimage_Index.zip), that describes the SPOT image extents, to a STAC. 

Usage:
```
stac spot convert-index [index location] [root_href]
```
