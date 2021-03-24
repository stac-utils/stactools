from typing import Callable, Optional

from lxml import etree
from pystac import STAC_IO

# Type alias
ReadHrefModifier = Callable[[str], str]


def read_xml(href: str, read_href_modifier: Optional[ReadHrefModifier] = None):
    if read_href_modifier is None:
        text = STAC_IO.read_text(href)
    else:
        text = STAC_IO.read_text(read_href_modifier(href))
    return etree.fromstring(bytes(text, encoding='utf-8'))


def convert(typ: Callable, v: Optional[str]) -> Optional[int]:
    return v if v is None else typ(v)


def band_index_to_name(index):
    raw_band_id = index + 1
    if raw_band_id == 9:
        band_id = '8A'
    elif raw_band_id > 9:
        band_id = str(raw_band_id - 1)
    else:
        band_id = str(raw_band_id)
    return f'B{band_id.rjust(2, "0")}'


def extract_gsd(image_path: str) -> float:
    return float(image_path[-7:-5])


def get_xml_node(root, xpath):
    return root.find(xpath, root.nsmap)


def list_xml_node(root, xpath):
    return root.findall(xpath, root.nsmap)


def get_xml_node_text(root: etree.ElementTree, xpath: str) -> Optional[str]:
    node = root.find(xpath, root.nsmap)
    if node is not None:
        return node.text
    return None


def get_xml_node_attr(root: etree.ElementTree,
                      attr: str,
                      xpath=None) -> Optional[str]:
    node = root
    if xpath is not None:
        node = root.find(xpath, root.nsmap)

    if node is not None:
        return node.get(attr)

    return None
