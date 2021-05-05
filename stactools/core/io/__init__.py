from typing import Callable, Optional

import pystac
import fsspec

ReadHrefModifier = Callable[[str], str]
"""Type alias for a function parameter
that allows users to manipulate HREFs for reading,
e.g. appending an Azure SAS Token or translating
to a signed URL
"""


def read_text(href: str,
              read_href_modifier: Optional[ReadHrefModifier]) -> str:
    if read_href_modifier is None:
        return pystac.STAC_IO.read_text(href)
    else:
        return pystac.STAC_IO.read_text(read_href_modifier(href))


def use_fsspec():
    # Use fsspec to handle IO
    def fsspec_read_method(uri):
        with fsspec.open(uri, 'r') as f:
            return f.read()

    def fsspec_write_method(uri, txt):
        with fsspec.open(uri, 'w') as f:
            return f.write(txt)

    pystac.STAC_IO.read_text_method = fsspec_read_method
    pystac.STAC_IO.write_text_method = fsspec_write_method
