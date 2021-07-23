from stactools.testing import TestData

test_data = TestData(
    __file__, {
        "item.json": {
            "url": "https://raw.githubusercontent.com/radiantearth/"
            "stac-spec/v1.0.0/examples/simple-item.json",
            "compress": False,
        },
        "goes-16/index.html": {
            "url": "s3://noaa-goes16/index.html",
        },
        "AW3D30_global.vrt": {
            "url": "s3://raster/AW3D30/AW3D30_global.vrt",
            "s3": {
                "anon": True,
                "client_kwargs": {
                    "endpoint_url": "https://opentopography.s3.sdsc.edu"
                }
            }
        }
    })
