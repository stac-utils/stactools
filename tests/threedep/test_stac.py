import unittest

from tests.utils import TestData
from stactools.threedep import stac


class CreateItemTest(unittest.TestCase):
    def test_create_item(self):
        path = TestData.get_path("data-files/threedep/base")
        item = stac.create_item("1", "n41w106", base_href=path)
        item.validate()
