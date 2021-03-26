from typing import List, Optional

from pystac import STAC_IO
from lxml import etree
from lxml.etree import _Element as lxmlElement

from stactools.core.io import ReadHrefModifier

class XmlElement:
    """Thin wrapper around lxml etree.Element with some
    convenience functions
    """
    def __init__(self, element: lxmlElement):
        self.element = element

    def find(self, xpath: str) -> Optional["XmlElement"]:
        node = self.element.find(xpath, self.element.nsmap)
        return None if node is None else XmlElement(node)


    def findall(self, xpath: str) -> List["XmlElement"]:
        return [XmlElement(e) for e in self.element.findall(xpath, self.element.nsmap)]


    def find_text(self, xpath: str) -> Optional[str]:
        node = self.find(xpath)
        return None if node is None else node.text

    def find_attr(self, attr: str, xpath: str) -> Optional[str]:
        node = self.find(xpath)
        return None if node is None else node.get_attr(attr)

    @property
    def text(self):
        return self.element.text

    def get_attr(self, attr: str) -> Optional[str]:
        return self.element.get(attr, None)


    @classmethod
    def from_file(cls, href: str, read_href_modifier: Optional[ReadHrefModifier] = None) -> "XmlElement":
        if read_href_modifier is None:
            text = STAC_IO.read_text(href)
        else:
            text = STAC_IO.read_text(read_href_modifier(href))
        return cls(etree.fromstring(bytes(text, encoding='utf-8')))
