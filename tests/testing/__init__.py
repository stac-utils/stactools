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
            "compress": False
        }
    })
