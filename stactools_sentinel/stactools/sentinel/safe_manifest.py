import os
from typing import Optional

import pystac

from stactools.sentinel.utils import read_xml, get_xml_node, get_xml_node_attr, ReadHrefModifier
from stactools.sentinel.constants import SAFE_MANIFEST_ASSET_KEY


class SafeManifest:
    def __init__(self,
                 granule_href: str,
                 read_href_modifier: Optional[ReadHrefModifier] = None):
        self.granule_href = granule_href
        self.href = os.path.join(granule_href, 'manifest.safe')

        root = read_xml(self.href, read_href_modifier)
        self._data_object_section = get_xml_node(root, 'dataObjectSection')

    @property
    def thumbnail_href(self) -> Optional[str]:
        thumbnail_path = get_xml_node_attr(
            self._data_object_section, 'href',
            'dataObject[@ID="S2_Level-1C_Preview_Tile1_Data"]/byteStream/fileLocation'
        )
        if thumbnail_path is None:
            thumbnail_path = get_xml_node_attr(
                self._data_object_section, 'href',
                'dataObject[@ID="Preview_4_Tile1_Data"]/byteStream/fileLocation'
            )

        if thumbnail_path is None:
            return None
        else:
            return os.path.join(self.granule_href, thumbnail_path)

    @property
    def product_metadata_href(self) -> Optional[str]:
        href = get_xml_node_attr(
            self._data_object_section, 'href',
            'dataObject[@ID="S2_Level-2A_Product_Metadata"]/byteStream/fileLocation'
        )

        if href is None:
            return None
        else:
            return os.path.join(self.granule_href, href)

    @property
    def inspire_metadata_href(self) -> Optional[str]:
        href = get_xml_node_attr(
            self._data_object_section, 'href',
            'dataObject[@ID="INSPIRE_Metadata"]/byteStream/fileLocation')

        if href is None:
            return None
        else:
            return os.path.join(self.granule_href, href)

    @property
    def datastrip_metadata_href(self) -> Optional[str]:
        href = get_xml_node_attr(
            self._data_object_section, 'href',
            'dataObject[@ID="S2_Level-2A_Datastrip1_Metadata"]/byteStream/fileLocation'
        )

        if href is None:
            return None
        else:
            return os.path.join(self.granule_href, href)

    @property
    def granule_metadata_href(self) -> Optional[str]:
        href = get_xml_node_attr(
            self._data_object_section, 'href',
            'dataObject[@ID="S2_Level-2A_Tile1_Data"]/byteStream/fileLocation')
        if href is None:
            href = get_xml_node_attr(
                self._data_object_section, 'href',
                'dataObject[@ID="S2_Level-2A_Tile1_Metadata"]/byteStream/fileLocation'
            )

        if href is None:
            return None
        else:
            return os.path.join(self.granule_href, href)

    def create_asset(self):
        asset = pystac.Asset(href=self.href,
                             media_type=pystac.MediaType.XML,
                             roles=['metadata'])
        return (SAFE_MANIFEST_ASSET_KEY, asset)
