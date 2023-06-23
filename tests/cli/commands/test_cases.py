import pystac

from tests import test_data


class TestCases:
    @staticmethod
    def planet_disaster() -> pystac.Collection:
        return pystac.Collection.from_file(
            test_data.get_path("data-files/planet-disaster/collection.json")
        )

    @staticmethod
    def basic_catalog() -> pystac.Catalog:
        return pystac.Catalog.from_file(
            test_data.get_path("data-files/basic/catalog.json")
        )
