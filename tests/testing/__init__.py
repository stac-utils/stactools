from stactools.testing import TestData

test_data = TestData(
    __file__, {
        "item.json": {
            "url": "https://raw.githubusercontent.com/radiantearth/"
            "stac-spec/v1.0.0/examples/simple-item.json",
            "compress": False,
        },
        "AW3D30_global.vrt": {
            "url": "s3://raster/AW3D30/AW3D30_global.vrt",
            "s3": {
                "anon": True,
                "client_kwargs": {
                    "endpoint_url": "https://opentopography.s3.sdsc.edu"
                }
            }
        },
        "manifest.safe": {
            "url":
            ("https://sentinel2l2a01.blob.core.windows.net/"
             "sentinel2-l2/03/K/TV/"
             "2020/05/23/"
             "S2A_MSIL2A_20200523T213041_N0212_R100_T03KTV_20200910T164427.SAFE/"
             "manifest.safe"),
            "planetary_computer":
            True
        }
    })
