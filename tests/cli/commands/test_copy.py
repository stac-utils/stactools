import os
from pathlib import Path

import pystac
import pystac.utils
from click.testing import CliRunner
from stactools.cli.cli import cli

from tests import test_data


def test_copy(tmp_path: Path, planet_disaster: pystac.Collection) -> None:
    collection_path = planet_disaster.get_self_href()
    item_ids = set([i.id for i in planet_disaster.get_items(recursive=True)])

    runner = CliRunner()
    result = runner.invoke(cli, ["copy", collection_path, str(tmp_path)])
    assert result.exit_code == 0

    copy_cat = pystac.read_file(tmp_path / "collection.json")
    copy_cat_ids = set([i.id for i in copy_cat.get_items(recursive=True)])

    assert copy_cat_ids == item_ids


def test_copy_to_relative(tmp_path: Path, planet_disaster: pystac.Collection) -> None:
    collection_path = planet_disaster.get_self_href()
    dst_dir = tmp_path / "second"

    runner = CliRunner()
    result = runner.invoke(
        cli, ["copy", "-t", "SELF_CONTAINED", "-a", collection_path, str(dst_dir)]
    )
    assert result.exit_code == 0

    dst_cat = pystac.read_file(dst_dir / "collection.json")
    for item in dst_cat.get_items(recursive=True):
        item_href = item.get_self_href()
        for asset in item.assets.values():
            href = asset.href
            assert pystac.utils.is_absolute_href(href) is False
            common_path = os.path.commonpath(
                [
                    os.path.dirname(item_href),
                    pystac.utils.make_absolute_href(href, item_href),
                ]
            )
            assert common_path == os.path.dirname(item_href)


def test_copy_using_publish_location(
    tmp_path: Path, planet_disaster: pystac.Collection
) -> None:
    collection_path = planet_disaster.get_self_href()
    href = "http://test.com"
    dst_dir = tmp_path / "second"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "copy",
            "-t",
            "ABSOLUTE_PUBLISHED",
            "-a",
            collection_path,
            str(dst_dir),
            "-l",
            href,
        ],
    )
    assert result.exit_code == 0

    dst_cat = pystac.read_file(dst_dir / "collection.json")

    for link in dst_cat.get_child_links():
        assert link.target.startswith(href)

    assert (
        dst_dir
        / "hurricane-harvey"
        / "hurricane-harvey-0831"
        / "Houston-East-20170831-103f-100d-0f4f-RGB"
        / "Houston-East-20170831-103f-100d-0f4f-3-band.tif"
    ).exists()


def test_move_assets(tmp_path: Path, planet_disaster: pystac.Collection) -> None:
    cat = planet_disaster
    cat.normalize_hrefs(str(tmp_path))
    cat.save(catalog_type=pystac.CatalogType.RELATIVE_PUBLISHED)
    cat_href = cat.get_self_href()

    runner = CliRunner()
    result = runner.invoke(cli, ["move-assets", "-c", cat_href])
    assert result.exit_code == 0

    cat2 = pystac.read_file(cat_href)
    for item in cat2.get_items(recursive=True):
        item_href = item.get_self_href()
        for asset in item.assets.values():
            href = asset.href

            assert pystac.utils.is_absolute_href(href) is False
            common_path = os.path.commonpath(
                [
                    os.path.dirname(item_href),
                    pystac.utils.make_absolute_href(href, item_href),
                ]
            )

            assert common_path == os.path.dirname(item_href)


def test_copy_assets(tmp_path: Path, planet_disaster: pystac.Collection) -> None:
    cat = planet_disaster
    cat_href = cat.get_self_href()

    runner = CliRunner()
    result = runner.invoke(cli, ["copy", cat_href, str(tmp_path), "-a"])
    assert result.exit_code == 0

    cat2 = pystac.read_file(tmp_path / "collection.json")
    for item in cat2.get_items(recursive=True):
        assert all(v.href.startswith("./") for v in item.assets.values())

    assert (
        tmp_path
        / "hurricane-harvey"
        / "hurricane-harvey-0831"
        / "Houston-East-20170831-103f-100d-0f4f-RGB"
        / "Houston-East-20170831-103f-100d-0f4f-3-band.tif"
    ).exists()


def test_copy_using_no_resolve_links(tmp_path: Path) -> None:
    cat_path = test_data.get_path("data-files/external-child/catalog.json")

    runner = CliRunner()
    result = runner.invoke(cli, ["copy", cat_path, str(tmp_path), "--no-resolve-links"])
    assert result.exit_code == 0

    assert os.listdir(tmp_path) == ["catalog.json"]


def test_copy_collection_with_assets(tmp_path: Path) -> None:
    cat_path = test_data.get_path("data-files/catalogs/collection-assets/catalog.json")

    runner = CliRunner()
    result = runner.invoke(cli, ["copy", cat_path, str(tmp_path), "-a"])
    assert result.exit_code == 0

    assert (tmp_path / "sentinel-2" / "metadata.xml").exists()
