import os
from pathlib import Path
from typing import List

import pystac
import pytest
from click.testing import CliRunner
from stactools.cli.cli import cli
from stactools.core import move_all_assets

from tests import test_data


@pytest.fixture(scope="function")
def two_planet_disaster_subsets(tmp_path: Path):
    """Fixture that makes two copies of subset of the planet
    disaster data, each containing a single item. Updates the collection
    extents to match the single items.

    Returns a list of collection paths in the temporary directory.
    """
    item_ids = ["20170831_172754_101c", "20170831_162740_ssc1d1"]
    new_cols = []
    for item_id in item_ids:
        col = pystac.Collection.from_file(
            test_data.get_path("data-files/planet-disaster/collection.json")
        )
        for item in list(col.get_all_items()):
            if item.id != item_id:
                item.get_parent().remove_item(item.id)
        col.update_extent_from_items()
        col.normalize_hrefs(str(tmp_path / item_id))
        col.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
        move_all_assets(col, copy=True)
        col.save()
        new_cols.append(col.get_self_href())

    return new_cols


def test_merge_moves_assets(two_planet_disaster_subsets: List[str]):
    col_paths = two_planet_disaster_subsets

    runner = CliRunner()
    result = runner.invoke(cli, ["merge", "-a", col_paths[0], col_paths[1]])
    assert result.exit_code == 0

    target_col = pystac.read_file(col_paths[1])

    items = list(target_col.get_all_items())
    assert len(items) == 2

    for item in items:
        for asset in item.assets.values():
            assert os.path.dirname(asset.get_absolute_href()) == os.path.dirname(
                item.get_self_href()
            )


def test_merge_as_child(two_planet_disaster_subsets: List[str]):
    col_paths = two_planet_disaster_subsets

    runner = CliRunner()
    result = runner.invoke(cli, ["merge", "-a", "-c", col_paths[0], col_paths[1]])
    assert result.exit_code == 0

    target_col = pystac.read_file(col_paths[1])

    links = list(target_col.get_child_links())
    assert len(links) == 2
    for child in links:
        assert os.path.exists(child.get_absolute_href())


def test_merge_updates_collection_extent(two_planet_disaster_subsets: List[str]):
    col_paths = two_planet_disaster_subsets
    extent1 = pystac.read_file(col_paths[0]).extent
    extent2 = pystac.read_file(col_paths[1]).extent

    xmin = min([extent1.spatial.bboxes[0][0], extent2.spatial.bboxes[0][0]])
    time_max = max(
        [
            extent1.temporal.intervals[0][1],
            extent2.temporal.intervals[0][1],
        ]
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["merge", col_paths[0], col_paths[1]])
    assert result.exit_code == 0

    result_extent = pystac.read_file(col_paths[1]).extent

    def set_of_values(x):
        result = set([])
        if type(x) is dict:
            result |= set_of_values(list(x.values()))
        elif type(x) is list:
            for e in x:
                if type(e) is list:
                    result |= set_of_values(e)
                else:
                    result.add(e)
        return result

    # Make sure it didn't just carry forward the old extent
    assert set_of_values(result_extent.spatial.bboxes) != set_of_values(
        extent2.spatial.bboxes
    )

    assert set_of_values(result_extent.temporal.intervals) != set_of_values(
        extent2.temporal.intervals
    )

    assert result_extent.spatial.bboxes[0][0] == xmin
    assert result_extent.temporal.intervals[0][1] == time_max


def test_merges_assets(tmp_path: Path, tmp_planet_disaster: pystac.Collection):
    col0 = tmp_planet_disaster
    item_id = "2017831_195552_SS02"

    item = col0.get_item(item_id, recursive=True)

    new_col1 = col0.clone()
    new_col1.clear_children()

    item1 = item.clone()
    del item1.assets["visual"]
    new_col1.add_item(item1)

    new_col1.normalize_hrefs(str(tmp_path / "a"))
    new_col1.save()

    new_col2 = col0.clone()
    new_col2.clear_children()

    item2 = item.clone()
    del item2.assets["full-jpg"]
    new_col2.add_item(item2)

    new_col2.normalize_hrefs(str(tmp_path / "b"))
    new_col2.save()

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "merge",
            str(tmp_path / "a" / "collection.json"),
            str(tmp_path / "b" / "collection.json"),
            "--move-assets",
            "--ignore-conflicts",
        ],
    )
    assert result.exit_code == 0

    target_col = pystac.read_file(str(tmp_path / "b" / "collection.json"))
    result_item = target_col.get_item(item_id, recursive=True)
    assert "visual" in result_item.assets
    assert "full-jpg" in result_item.assets
