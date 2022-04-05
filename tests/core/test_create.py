import os.path
from unittest import TestCase

from pystac.extensions.projection import ProjectionExtension

from stactools.core import create
from tests import test_data


class CreateItem(TestCase):
    def setUp(self) -> None:
        self.path = test_data.get_path(
            "data-files/planet-disaster/hurricane-harvey/"
            "hurricane-harvey-0831/20170831_172754_101c/20170831_172754_101c_3b_Visual.tif"
        )

    def test_one_datetime(self) -> None:
        item = create.item(self.path)
        self.assertEqual(item.id, os.path.splitext(os.path.basename(self.path))[0])
        self.assertIsNotNone(item.datetime)
        self.assertEqual(
            item.geometry,
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-95.780872, 29.517294],
                        [-95.783782, 29.623358],
                        [-96.041791, 29.617689],
                        [-96.038613, 29.511649],
                        [-95.780872, 29.517294],
                    ]
                ],
            },
        )
        self.assertEqual(item.bbox, [-96.041791, 29.511649, -95.780872, 29.623358])
        self.assertIsNone(item.common_metadata.start_datetime)
        self.assertIsNone(item.common_metadata.end_datetime)

        projection = ProjectionExtension.ext(item)
        self.assertEqual(projection.epsg, 32615)
        self.assertIsNone(projection.wkt2)
        self.assertIsNone(projection.projjson)
        self.assertEqual(
            projection.transform,
            [97.69921875, 0.0, 205437.0, 0.0, -45.9609375, 3280290.0],
        )
        self.assertEqual(projection.shape, (256, 256))

        data = item.assets["data"]
        self.assertEqual(data.href, self.path)
        self.assertIsNone(data.title)
        self.assertIsNone(data.description)
        self.assertEqual(data.roles, ["data"])
        self.assertEqual(data.media_type, None)
        item.validate()

    def test_read_href_modifer(self) -> None:
        did_it = False

        def do_it(href: str) -> str:
            nonlocal did_it
            did_it = True
            return href

        item = create.item(self.path, read_href_modifier=do_it)
        assert did_it
        assert item.id == "20170831_172754_101c_3b_Visual"
