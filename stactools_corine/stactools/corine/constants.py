import pystac

provider_name = 'European Environment Agency (EEA) under the framework of the Copernicus programme'

COPERNICUS_PROVIDER = pystac.Provider(name=provider_name,
                                      url=('http://www.eea.europa.eu'),
                                      roles=['producer', 'licensor'])

ITEM_COG_IMAGE_NAME = 'cog_image'
ITEM_TIF_IMAGE_NAME = 'tif_image'
ITEM_METADATA_NAME = 'metadata'
