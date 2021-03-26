from typing import Callable

import pystac
import fsspec


ReadHrefModifier = Callable[[str], str]
"""Type alias for a function parameter
that allows users to manipulate HREFs for reading,
e.g. appending an Azure SAS Token or translating
to a signed URL
"""


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
