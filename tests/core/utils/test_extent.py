import json

import pystac

from stactools.core import use_fsspec
from stactools.core.utils.extent import update_geometry_from_asset_extent
from tests import test_data


def test_x():
    use_fsspec()

    item = pystac.read_file(
        test_data.get_path(
            "data-files/extent/MCD43A4.A2001055.h25v06.006.2016113010159.json"
        )
    )

    item = update_geometry_from_asset_extent(item, ["B01"], tolerance=0.00005)

    print(json.dumps(item.to_dict()))
