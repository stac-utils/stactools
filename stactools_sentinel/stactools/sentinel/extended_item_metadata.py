import pystac
from pystac import (STACObject, Link)


class ExtendedItemMetadata(STACObject):
    def __init__(self, item, additional_properties={}):
        super().__init__(item.stac_extensions)

        self.item = item
        self.additional_properties = additional_properties
        self.id = item.id
        self.stac_version = item.stac_version
        self.datetime = item.datetime
        self.properties = {**item.properties, **additional_properties}
        self.add_link(Link("extends", item, pystac.MediaType.JSON))

    def _object_links(self):
        return ['collection'] + (pystac.STAC_EXTENSIONS.get_extended_object_links(self))

    def clone(self):
        return ExtendedItemMetadata(self.item, self.additional_properties)

    def from_dict(cls, d, href=None, root=None):
        d = deepcopy(d)
        id = d.pop('id')
        geometry = d.pop('geometry')
        properties = d.pop('properties')
        bbox = d.pop('bbox', None)
        stac_extensions = d.get('stac_extensions')
        collection_id = d.pop('collection', None)

        datetime = properties.get('datetime')
        if datetime is not None:
            datetime = dateutil.parser.parse(datetime)
        links = d.pop('links')
        assets = d.pop('assets')

        d.pop('type')
        d.pop('stac_version')

        item = Item(id=id,
                    geometry=geometry,
                    bbox=bbox,
                    datetime=datetime,
                    properties=properties,
                    stac_extensions=stac_extensions,
                    collection=collection_id,
                    extra_fields=d)

        has_self_link = False
        for link in links:
            has_self_link |= link['rel'] == 'self'
            item.add_link(Link.from_dict(link))

        if not has_self_link and href is not None:
            item.add_link(Link.self_href(href))

        for k, v in assets.items():
            asset = Asset.from_dict(v)
            asset.set_owner(item)
            item.assets[k] = asset

        return item
    def to_dict:
