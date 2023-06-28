import pystac
import pytest

from tests.testing import test_data


def test_external_data_https():
    path = test_data.get_external_data("item.json")
    item = pystac.read_file(path)
    assert "20201211_223832_CS2" == item.id


def test_external_data_s3():
    pytest.importorskip("s3fs")
    path = test_data.get_external_data("AW3D30_global.vrt")
    with open(path) as f:
        xml = f.read()
    assert (
        xml.find("ALPSMLC30_N041W106_DSM") != -1
    ), "Could not find 'ALPSMLC30_N041W106_DSM' in the ALOS VRT"


def test_external_pc_data():
    path = test_data.get_external_data("manifest.safe")
    with open(path) as f:
        xml = f.read()
    assert xml is not None
