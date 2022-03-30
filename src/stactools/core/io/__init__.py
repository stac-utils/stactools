import hashlib
from dataclasses import dataclass
from typing import Any, Callable, Optional, cast

import fsspec
import multihash
from pystac.stac_io import DefaultStacIO, StacIO

from stactools.core import utils

ReadHrefModifier = Callable[[str], str]
"""Type alias for a function parameter
that allows users to manipulate HREFs for reading,
e.g. appending an Azure SAS Token or translating
to a signed URL
"""


def read_text(href: str, read_href_modifier: Optional[ReadHrefModifier] = None) -> str:
    if read_href_modifier is None:
        return StacIO.default().read_text(href)
    else:
        return StacIO.default().read_text(read_href_modifier(href))


class FsspecStacIO(DefaultStacIO):
    def read_text_from_href(self, href: str, *args: Any, **kwargs: Any) -> str:
        with fsspec.open(href, "r") as f:
            s = f.read()
            if isinstance(s, str):
                return s
            elif isinstance(s, bytes):
                return str(s, encoding="utf-8")
            else:
                raise ValueError(f"Unable to decode data loaded from HREF: {href}")

    def write_text_from_href(
        self, href: str, txt: str, *args: Any, **kwargs: Any
    ) -> None:
        utils.deprecate(
            "FsspecStacIO.write_text_from_href",
            "FsspecStacIO.write_text_to_href",
            "v0.5.0",
        )
        return self.write_text_to_href(href, txt)

    def write_text_to_href(self, href: str, txt: str) -> None:
        """Writes text to an href using fsspec."""
        with fsspec.open(href, "w") as destination:
            destination.write(txt)


def use_fsspec() -> None:
    StacIO.set_default(FsspecStacIO)


@dataclass
class FileInfo:

    checksum: str
    size: int

    @classmethod
    def read(cls, href: str) -> "FileInfo":
        m = hashlib.sha256()
        with fsspec.open(href, mode="rb") as file:
            data = file.read()
            size = len(data)
            m.update(data)
        hash = multihash.encode(m.digest(), code="sha2-256", length=m.digest_size)
        checksum = cast(str, multihash.to_hex_string(hash))
        return FileInfo(checksum=checksum, size=size)
