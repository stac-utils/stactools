from typing import Callable, Optional, Any

from pystac.stac_io import DefaultStacIO, StacIO
import fsspec

ReadHrefModifier = Callable[[str], str]
"""Type alias for a function parameter
that allows users to manipulate HREFs for reading,
e.g. appending an Azure SAS Token or translating
to a signed URL
"""


def read_text(href: str,
              read_href_modifier: Optional[ReadHrefModifier] = None) -> str:
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
                return str(s, encoding='utf-8')
            else:
                raise ValueError(
                    f"Unable to decode data loaded from HREF: {href}")

    def write_text_from_href(self, href: str, txt: str, *args: Any,
                             **kwargs: Any) -> None:
        with fsspec.open(href, "w") as destination:
            destination.write(txt)


def use_fsspec() -> None:
    StacIO.set_default(FsspecStacIO)
