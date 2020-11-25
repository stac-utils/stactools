import os

import pystac
from pystac.utils import (str_to_datetime, make_absolute_href)
import rasterio as rio
from shapely.geometry import box, mapping, shape

from stactools.aster.constants import (HDF_ASSET_KEY, ASTER_BANDS)
from stactools.aster.utils import (AsterSceneId,
                                   epsg_from_aster_utm_zone_number)

ASTER_PROVIDER = pystac.Provider(
    name='NASA LP DAAC at the USGS EROS Center',
    url='https://doi.org/10.5067/ASTER/AST_L1T.003',
    roles=['producer', 'processor', 'licensor'])


# TODO: Integrate XML data; for instance, XML has most up-to-date
# cloud cover information.
def create_item(hdf_path, additional_providers=None):
    file_name = os.path.basename(hdf_path)
    scene_id = AsterSceneId.from_path(file_name)

    with rio.open(hdf_path) as f:
        tags = f.tags()

    xmin, xmax = float(tags.pop('WESTBOUNDINGCOORDINATE')), float(
        tags.pop('EASTBOUNDINGCOORDINATE'))
    ymin, ymax = float(tags.pop('SOUTHBOUNDINGCOORDINATE')), float(
        tags.pop('NORTHBOUNDINGCOORDINATE'))
    geom = mapping(box(xmin, ymin, xmax, ymax))
    bounds = shape(geom).bounds

    dt = str_to_datetime(tags.pop('SETTINGTIMEOFPOINTING.1'))

    item = pystac.Item(
        id=scene_id.item_id,
        geometry=geom,
        bbox=bounds,
        datetime=dt,
        properties={'aster:processing_number': scene_id.processing_number})

    # Common metadata
    item.common_metadata.providers = [ASTER_PROVIDER]
    if additional_providers is not None:
        item.common_metadata.providers.extend(additional_providers)
    item.common_metadata.created = str_to_datetime(
        tags.pop('PRODUCTIONDATETIME'))
    item.common_metadata.platform = tags.pop('PLATFORMSHORTNAME')
    item.common_metadata.instruments = [tags.pop('INSTRUMENTSHORTNAME')]

    # eo
    item.ext.enable('eo')
    # STAC uses 0-100, planet 0-1
    item.ext.eo.cloud_cover = int(tags.pop('SCENECLOUDCOVERAGE'))

    # view
    item.ext.enable('view')
    # Don't pop, to keep the 3 values in properties.
    item.ext.view.off_nadir = abs(float(tags['POINTINGANGLE.1']))
    sun_azimuth, sun_elevation = [
        float(x) for x in tags['SOLARDIRECTION'].split(', ')
    ]
    item.ext.view.sun_azimuth = float(sun_azimuth)
    # Sun elevation can be negative; if so, will break validation; leave out.
    # See https://github.com/radiantearth/stac-spec/issues/853
    sun_elevation = float(sun_elevation)
    if sun_elevation >= 0.0:
        item.ext.view.sun_elevation = float(sun_elevation)

    # proj
    item.ext.enable('projection')
    item.ext.projection.epsg = epsg_from_aster_utm_zone_number(
        int(tags.pop('UTMZONENUMBER')))

    # Add all additional properties with Planet extension designation.
    for k, v in tags.items():
        item.properties['aster:{}'.format(k)] = v

    hdf_href = make_absolute_href(hdf_path)

    asset = pystac.Asset(href=hdf_href,
                         media_type=pystac.MediaType.HDF,
                         roles=['data'],
                         title="ASTER L1T 003 HDF-EOS")

    item.ext.eo.set_bands(ASTER_BANDS, asset)

    item.add_asset(HDF_ASSET_KEY, asset)

    return item
