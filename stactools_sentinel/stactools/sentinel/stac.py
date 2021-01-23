import os

import pystac

SENTINEL_PROVIDER = pystac.Provider(
    name='ESA',
    roles=['producer', 'processor', 'licensor'],
    url='https://earth.esa.int/web/guest/home'
)


def create_item(granule_path, additional_providers=None):
    file_name = os.path.basename(granule_path)
    scene_id = 123
