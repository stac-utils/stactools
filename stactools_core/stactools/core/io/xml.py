from functools import lru_cache
from typing import Callable, List, Optional

from lxml import etree
from lxml.etree import _Element as lxmlElement

from stactools.core.io import ReadHrefModifier, read_text


class XmlElement:
    """Thin wrapper around lxml etree.Element with some
    convenience functions
    """
    def __init__(self, element: lxmlElement):
        self.element = element

    @lru_cache(maxsize=100)
    def find(self, xpath: str) -> Optional["XmlElement"]:
        node = self.element.find(xpath, self.element.nsmap)
        return None if node is None else XmlElement(node)

    def find_or_throw(
            self, xpath: str,
            get_exception: Callable[[str], Exception]) -> "XmlElement":
        result = self.find(xpath)
        if result is None:
            raise get_exception(xpath)
        return result

    @lru_cache(maxsize=100)
    def findall(self, xpath: str) -> List["XmlElement"]:
        return [
            XmlElement(e)
            for e in self.element.findall(xpath, self.element.nsmap)
        ]

    @lru_cache(maxsize=100)
    def find_text(self, xpath: str) -> Optional[str]:
        node = self.find(xpath)
        return None if node is None else node.text

    def find_text_or_throw(self, xpath: str,
                           get_exception: Callable[[str], Exception]) -> str:
        result = self.find_text(xpath)
        if result is None:
            raise get_exception(xpath)
        return result

    @lru_cache(maxsize=100)
    def find_attr(self, attr: str, xpath: str) -> Optional[str]:
        node = self.find(xpath)
        return None if node is None else node.get_attr(attr)

    @property
    def text(self):
        return self.element.text

    @lru_cache(maxsize=100)
    def get_attr(self, attr: str) -> Optional[str]:
        return self.element.get(attr, None)

    @classmethod
    def from_file(cls,
                  href: str,
                  read_href_modifier: Optional[ReadHrefModifier] = None
                  ) -> "XmlElement":
        text = read_text(href, read_href_modifier)
        return cls(etree.fromstring(bytes(text, encoding='utf-8')))
