from pystac.extensions.eo import Band

L8_PLATFORM = "landsat-8"
L8_INSTRUMENTS = ["oli", "tirs"]

L8_EXTENSION_SCHEMA = "https://landsat.usgs.gov/stac/landsat-extension/schema.json"
L8_ITEM_DESCRIPTION = "Landsat Collection 2 Level-2 Surface Reflectance Product"

L8_SR_BANDS = {
    "SR_B1":
    Band({
        "name": "SR_B1",
        "common_name": "coastal",
        "gsd": 30,
        "center_wavelength": 0.44,
        "full_width_half_max": 0.02
    }),
    "SR_B2":
    Band({
        "name": "SR_B2",
        "common_name": "blue",
        "gsd": 30,
        "center_wavelength": 0.48,
        "full_width_half_max": 0.06
    }),
    "SR_B3":
    Band({
        "name": "SR_B3",
        "common_name": "green",
        "gsd": 30,
        "center_wavelength": 0.56,
        "full_width_half_max": 0.06
    }),
    "SR_B4":
    Band({
        "name": "SR_B4",
        "common_name": "red",
        "gsd": 30,
        "center_wavelength": 0.65,
        "full_width_half_max": 0.04
    }),
    "SR_B5":
    Band({
        "name": "SR_B5",
        "common_name": "nir08",
        "gsd": 30,
        "center_wavelength": 0.86,
        "full_width_half_max": 0.03
    }),
    "SR_B6":
    Band({
        "name": "SR_B6",
        "common_name": "swir16",
        "gsd": 30,
        "center_wavelength": 1.6,
        "full_width_half_max": 0.08
    }),
    "SR_B7":
    Band({
        "name": "SR_B7",
        "common_name": "swir22",
        "gsd": 30,
        "center_wavelength": 2.2,
        "full_width_half_max": 0.2
    })
}

L8_SP_BANDS = {
    # L2SP only bands

    #  ST_B10 Note:
    # Changed common_name from UGSG STAC - should be lwir11 based on wavelength
    # Also, resolution at sensor is 100m, even though the raster is 30m pixel width/height.
    "ST_B10":
    Band({
        "name": "ST_B10",
        "common_name": "lwir11",
        "gsd": 100.0,
        "center_wavelength": 10.9,
        "full_width_half_max": 0.8
    }),
    "ST_ATRAN":
    Band({
        "name": "ST_ATRAN",
        "description": "atmospheric transmission",
        "gsd": 30
    }),
    "ST_CDIST":
    Band({
        "name": "ST_CDIST",
        "description": "distance to nearest cloud",
        "gsd": 30
    }),
    "ST_DRAD":
    Band({
        "name": "ST_DRAD",
        "description": "downwelled radiance",
        "gsd": 30
    }),
    "ST_URAD":
    Band({
        "name": "ST_URAD",
        "description": "upwelled radiance",
        "gsd": 30
    }),
    "ST_TRAD":
    Band({
        "name": "ST_TRAD",
        "description": "thermal radiance",
        "gsd": 30
    }),
    "ST_EMIS":
    Band({
        "name": "ST_EMIS",
        "description": "emissivity",
        "gsd": 30
    }),
    "ST_EMSD":
    Band({
        "name": "ST_EMSD",
        "description": "emissivity standard deviation",
        "gsd": 30
    })
}
