from typing import Callable, Optional, TYPE_CHECKING, Union, Any

from pystac import StacIO
import fsspec

if TYPE_CHECKING:
    from pystac.link import Link as Link_Type

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


class FsspecStacIO(StacIO):
    def read_text(self, source: Union[str, "Link_Type"], *args: Any,
                  **kwargs: Any) -> str:
        if isinstance(source, str):
            href = source
        else:
            href = source.get_absolute_href()
            if href is None:
                raise IOError(
                    f"Could not get an absolute HREF from link {source}")
        with fsspec.open(href, "r") as f:
            return f.read()

    def write_text(self, dest: Union[str, "Link_Type"], txt: str, *args: Any,
                   **kwargs: Any) -> None:
        if isinstance(dest, str):
            href = dest
        else:
            href = dest.get_absolute_href()
            if href is None:
                raise IOError(
                    f"Could not get an absolute HREF from link {dest}")
        with fsspec.open(href, "w") as destination:
            return destination.write(txt)


def use_fsspec():
    StacIO.set_default(FsspecStacIO)
