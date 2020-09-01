import pystac
import fsspec


def use_fsspec():
    # Use fsspec to handle IO
    def fsspec_read_method(uri):
        with fsspec.open(uri) as f:
            return f.read()

    def fsspec_write_method(uri, txt):
        with fsspec.open(uri, 'w') as f:
            return f.write(txt)

    pystac.STAC_IO.read_text_method = fsspec_read_method
    pystac.STAC_IO.write_text_method = fsspec_write_method
