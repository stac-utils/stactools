PROVIDER_NAME = 'European Environment Agency (EEA) under the framework of the Copernicus programme'

ITEM_COG_IMAGE_NAME = 'cog_image'
ITEM_TIF_IMAGE_NAME = 'tif_image'

DISCRETE_CLASSIFICATION_CLASS_NAMES = {
    0: "Unknown.",
    20:
    """Shrubs. Woody perennial plants with persistent and woody stems and without
         any defined main stem being less than 5 m tall. The shrub foliage can be either
         evergreen or deciduous.""",
    30:
    """Herbaceous vegetation. Plants without persistent stem or shoots above ground and
         lacking definite firm structure. Tree and shrub cover is less than 10 %.""",
    40:
    """Cultivated and managed vegetation / agriculture. Lands covered with temporary crops
         followed by harvest and a bare soil period (e.g., single and multiple cropping systems).
         Note that perennial woody crops will be classified as the appropriate forest or shrub
         land cover type.""",
    50:
    "Urban / built up. Land covered by buildings and other man-made structures.",
    60:
    """Bare / sparse vegetation. Lands with exposed soil, sand, or rocks and never has more
         than 10 % vegetated cover during any time of the year.""",
    70: "Snow and ice. Lands under snow or ice cover throughout the year.",
    80:
    """Permanent water bodies. Lakes, reservoirs, and rivers. Can be either fresh or
         salt-water bodies.""",
    90:
    """Herbaceous wetland. Lands with a permanent mixture of water and herbaceous or woody
         vegetation. The vegetation can be present in either salt, brackish, or fresh water.""",
    100: "Moss and lichen.",
    111:
    """Closed forest, evergreen needle leaf. Tree canopy >70 %, almost all needle leaf trees
         remain green all year. Canopy is never without green foliage.""",
    112:
    """Closed forest, evergreen broad leaf. Tree canopy >70 %, almost all broadleaf trees remain
         green year round. Canopy is never without green foliage.""",
    113:
    """Closed forest, deciduous needle leaf. Tree canopy >70 %, consists of seasonal needle
         leaf tree communities with an annual cycle of leaf-on and leaf-off periods.""",
    114:
    """Closed forest, deciduous broad leaf. Tree canopy >70 %, consists of seasonal broadleaf
         tree communities with an annual cycle of leaf-on and leaf-off periods.""",
    115: "Closed forest, mixed.",
    116: "Closed forest, not matching any of the other definitions.",
    121:
    """Open forest, evergreen needle leaf. Top layer- trees 15-70 and second layer- mixed of
         shrubs and grassland, almost all needle leaf trees remain green all year. Canopy is never
         without green foliage.""",
    122:
    """Open forest, evergreen broad leaf. Top layer- trees 15-70 and second layer- mixed of
         shrubs and grassland, almost all broadleaf trees remain green year round. Canopy is never
         without green foliage.""",
    123:
    """Open forest, deciduous needle leaf. Top layer- trees 15-70 and second layer- mixed of
         shrubs and grassland, consists of seasonal needle leaf tree communities with an
         annual cycle of leaf-on and leaf-off periods.""",
    124:
    """Open forest, deciduous broad leaf. Top layer- trees 15-70 and second layer- mixed of
         shrubs and grassland, consists of seasonal broadleaf tree communities with an
         annual cycle of leaf-on and leaf-off periods.""",
    125: "Open forest, mixed.",
    126: "Open forest, not matching any of the other definitions.",
    200: "Oceans, seas. Can be either fresh or salt-water bodies."
}

DISCRETE_CLASSIFICATION_CLASS_PALETTE = {
    0: '282828',
    1: 'FFBB22',
    2: 'FFFF4C',
    3: 'F096FF',
    4: 'FA0000',
    5: 'B4B4B4',
    6: 'F0F0F0',
    7: '0032C8',
    8: '0096A0',
    9: 'FAE6A0',
    10: '58481F',
    11: '009900',
    12: '70663E',
    13: '00CC00',
    14: '4E751F',
    15: '007800',
    16: '666000',
    17: '8DB400',
    18: '8D7400',
    19: 'A0DC00',
    20: '929900',
    21: '648C00',
    22: '000080'
}
