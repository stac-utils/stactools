from functools import lru_cache
from typing import Any, Callable, List, Optional, cast

from lxml import etree
from lxml.etree import _Element as lxmlElement

from stactools.core.io import ReadHrefModifier, read_text


class XmlElement:
    """Thin wrapper around `lxml <https://lxml.de/>`_ etree.Element with some
    convenience functions."""

    def __init__(self, element: lxmlElement):
        """Creates a new ``XmlElement`` by wrapping an ``lxml.etree._Element``.

        Args:
            element (lxmlElement): The ``lxml`` element to wrap.
        """
        self.element = element

    @lru_cache(maxsize=100)
    def find(self, xpath: str) -> Optional["XmlElement"]:
        """Find a child ``XmlElement`` by xpath.

        Args:
            xpath (str): The xpath to use for search.

        Returns:
            Optional[XmlElement]: The found element, or None if not found.
        """
        node = self.element.find(xpath, self.element.nsmap)  # type: ignore
        return None if node is None else XmlElement(node)

    def find_or_throw(
        self, xpath: str, get_exception: Callable[[str], Exception]
    ) -> "XmlElement":
        """Find a child ``XmlElement`` by xpath, or throw an exception if not
        found.

        Args:
            xpath (str): The xpath to use for search.
            get_exception (Callable[[str], Exception]):
                A callable that builds the exception to be thrown when the xpath
                does not match any elements.

        Returns:
            XmlElement: The child xml element identified by the xpath.

        Raises:
            Exception: If no element is found.
        """
        result = self.find(xpath)
        if result is None:
            raise get_exception(xpath)
        return result

    @lru_cache(maxsize=100)
    def findall(self, xpath: str) -> List["XmlElement"]:
        """Finds all children that match the given xpath.

        Args:
            xpath (str): The xpath to use for search.

        Returns:
            list[XmlElement]: The found elements.
        """
        return [
            XmlElement(e)
            for e in self.element.findall(xpath, self.element.nsmap)  # type: ignore
        ]

    @lru_cache(maxsize=100)
    def find_text(self, xpath: str) -> Optional[str]:
        """Finds an element by xpath and returns its contained text.

        Args:
            xpath (str): The xpath to use for search.

        Returns:
            Optional[str]:
                The text inside of the found element, or None if the
                element was not found.
        """
        node = self.find(xpath)
        return None if node is None else node.text

    def find_text_or_throw(
        self, xpath: str, get_exception: Callable[[str], Exception]
    ) -> str:
        """Finds an element by xpath and returns its contained text, or throws
        an error if no element is found.

        Args:
            xpath (str): The xpath to use for search.
            get_exception (Callable[[str], Exception]):
                A callable that builds the exception to be thrown when the xpath
                does not match any elements.

        Returns:
            Optional[str]:
                The text inside of the found element, or None if the
                element was not found.

        Raises:
            Exception: If no element is found.
        """

        result = self.find_text(xpath)
        if result is None:
            raise get_exception(xpath)
        return result

    @lru_cache(maxsize=100)
    def find_attr(self, attr: str, xpath: str) -> Optional[str]:
        """Finds and returns an attribute of an element.

        Args:
            attr (str): The attribute name.
            xpath (str): The xpath of the element to find.

        Returns:
            Optional[str]:
                The value of the attribute, or None if the element
                was not found.
        """
        node = self.find(xpath)
        return None if node is None else node.get_attr(attr)

    @property
    def text(self) -> Optional[str]:
        """Returns the text of this element.

        Returns:
            Optional[str]:
                The text value of this element, decoded as utf-8 if
                necessary, or None if there is no text.
        """
        if isinstance(self.element.text, str):
            return self.element.text
        elif isinstance(self.element.text, bytes):
            return str(self.element.text, encoding="utf-8")
        else:
            assert self.element.text is None
            return None

    @lru_cache(maxsize=100)
    def get_attr(self, attr: str) -> Optional[str]:
        """Returns the value of a given attribute of this element.

        Args:
            attr (str): The name of the attribute.

        Returns:
            Optional[str]:
                The value of the attribute, or None if the attribute is not
                present on this element.
        """
        return cast(Optional[str], self.element.get(attr, None))

    @classmethod
    def from_file(
        cls,
        href: str,
        read_href_modifier: Optional[ReadHrefModifier] = None,
        **kwargs: Any,
    ) -> "XmlElement":
        """Reads an XmlElement from an href.

        Optionally modifies the href with ``read_href_modifier``. Uses
        :py:meth:`stactools.core.io.read_text` to read the text.

        Args:
            href (str): The href to read.
            read_href_modifier (Optional[:class:`stactools.core.io.ReadHrefModifier`]):
                An optional callable that will be used to modify the href.
                Defaults to None.

        Returns:
            XmlElement: The read XmlElement.
        """
        text = read_text(href, read_href_modifier, **kwargs)
        return cls(etree.fromstring(bytes(text, encoding="utf-8")))
