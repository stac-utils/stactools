import json
import os

import fsspec
import pystac
from pystac.utils import make_absolute_href

from stactools.planet import (PlanetItem, PLANET_PROVIDER)


class OrderManifest:
    def __init__(self, manifest_dict, base_dir):
        self.manifest_dict = manifest_dict
        self.base_dir = base_dir

    def get_planet_items(self):
        # Group by planet item ID
        items_by_id = {}
        for f in self.manifest_dict['files']:
            item_id = f['annotations']['planet/item_id']
            if item_id not in items_by_id:
                items_by_id[item_id] = {'metadata': None, 'assets': []}
            entry = items_by_id[item_id]
            if f['path'].endswith('metadata.json'):
                if entry['metadata'] is not None:
                    raise Exception(
                        'Duplicate metadata found for item {}'.format(item_id))
                entry['metadata'] = os.path.join(self.base_dir, f['path'])
            else:
                entry['assets'].append(f)

        return [
            PlanetItem.from_file(i['metadata'], i['assets'], self.base_dir)
            for i in items_by_id.values()
        ]

    def to_stac(self, collection_id, description=None, title=None):
        planet_items = self.get_planet_items()
        stac_items = [i.to_stac() for i in planet_items]

        extent = pystac.Extent.from_items(stac_items)

        collection = pystac.Collection(id=collection_id,
                                       description=description,
                                       title=title,
                                       extent=extent,
                                       providers=[PLANET_PROVIDER])
        collection.add_items(stac_items)

        return collection

    @classmethod
    def from_file(cls, uri):
        with fsspec.open(uri) as f:
            return cls(json.load(f), make_absolute_href(os.path.dirname(uri)))
