import pystac
import pystac.utils
from click.testing import CliRunner

from stactools.cli.cli import cli
from tests.conftest import expected_json


def test_add_raster_to_items(tmp_planet_disaster: pystac.Collection):
    collection = tmp_planet_disaster
    collection_path = collection.get_self_href()
    items = list(collection.get_items(recursive=True))
    item_path = pystac.utils.make_absolute_href(
        items[0].get_self_href(), collection_path
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["add-raster", item_path])
    assert result.exit_code == 0

    updated = pystac.read_file(collection_path)
    item = list(updated.get_items(recursive=True))[0]
    asset = item.get_assets().get("analytic")
    assert asset is not None
    expected = expected_json("rasterbands.json")
    for a, b in zip(expected, asset.to_dict().get("raster:bands")):
        assert a == b
