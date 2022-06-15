"""Input/output utility functions and definitions."""

from typing import Callable, Optional

import fsspec
from pystac.stac_io import DefaultStacIO, StacIO

from stactools.core import utils

ReadHrefModifier = Callable[[str], str]
"""Type alias for a function parameter that allows users to manipulate HREFs.

Used for reading, e.g. appending an Azure SAS Token or translating to a signed URL.
"""


def read_text(href: str, read_href_modifier: Optional[ReadHrefModifier] = None) -> str:
    """Reads a string from an href.

    If ``read_href_modifier`` is provided, then ``href`` will be passed through
    this function before use. This function uses the default
    :py:class:`pystac.StacIO`.

    Args:
        href (str): The href to be read
        read_href_modifier (ReadHrefModifier, optional):
            A function to modify
            the provided href. Defaults to None.

    Returns:
        str: The text as read from the href.
    """
    if read_href_modifier is None:
        return StacIO.default().read_text(href)
    else:
        return StacIO.default().read_text(read_href_modifier(href))


class FsspecStacIO(DefaultStacIO):
    """A subclass of :py:class:`pystac.DefaultStacIO` that uses `fsspec
    <https://filesystem-spec.readthedocs.io/en/latest/>`_ for reads and writes.
    """

    def read_text_from_href(self, href: str) -> str:
        """Reads a file as a utf-8 string using `fsspec
        <https://filesystem-spec.readthedocs.io/en/latest/>`_

        Args:
            href (str): The href to read.

        Returns:
            str: The read text, decoded as utf-8 if necessary.
        """
        with fsspec.open(href, "r") as f:
            s = f.read()
            if isinstance(s, str):
                return s
            elif isinstance(s, bytes):
                return str(s, encoding="utf-8")
            else:
                raise ValueError(f"Unable to decode data loaded from HREF: {href}")

    def write_text_from_href(self, href: str, txt: str) -> None:
        utils.deprecate(
            "FsspecStacIO.write_text_from_href",
            "FsspecStacIO.write_text_to_href",
            "v0.5.0",
        )
        return self.write_text_to_href(href, txt)

    def write_text_to_href(self, href: str, txt: str) -> None:
        """Writes text to an href using fsspec.

        Args:
            href (str): The href to write to.
            txt (str): The text to write.
        """
        with fsspec.open(href, "w") as destination:
            destination.write(txt)


def use_fsspec() -> None:
    """Sets the default :py:class:`pystac.StacIO` to :py:class:`FsspecStacIO`."""
    StacIO.set_default(FsspecStacIO)
