import unittest

from stactools.naip.stac import create_collection


class StacTest(unittest.TestCase):
    def test_create_collection(self):
        collection = create_collection(seasons=[2011, 2013, 2015, 2017, 2019])

        collection.set_self_href('http://example.com/collection.json')
        collection.validate()
