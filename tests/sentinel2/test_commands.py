import os
from tempfile import TemporaryDirectory

import pystac
from shapely.geometry import box, shape, mapping

from stactools.core.projection import reproject_geom
from stactools.sentinel2.commands import create_sentinel2_command
from tests.utils import (TestData, CliTestCase)


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_sentinel2_command]

    def test_create_item(self):
        granule_hrefs = [
            TestData.get_path(f'data-files/sentinel2/{x}') for x in [
                'S2A_MSIL2A_20190212T192651_N0212_R013_T07HFE_20201007T160857.SAFE',
                'S2B_MSIL2A_20191228T210519_N0212_R071_T01CCV_20201003T104658.SAFE',
                'esa_S2B_MSIL2A_20210122T133229_N0214_R081_T22HBD_20210122T155500.SAFE'
            ]
        ]

        def check_proj_bbox(item):
            pb = mapping(
                box(*item.ext.projection.get_bbox(item.assets['visual-10m'])))
            proj_geom = shape(
                reproject_geom(f'epsg:{item.ext.projection.epsg}', 'epsg:4326',
                               pb))

            item_geom = shape(item.geometry)

            difference_area = item_geom.difference(proj_geom).area
            raster_area = proj_geom.area

            # We expect the footprint to be in the raster
            # bounds, so any difference should be relatively very low
            # and due to reprojection.
            self.assertLess(difference_area / raster_area, 0.005)

        for granule_href in granule_hrefs:
            with self.subTest(granule_href):
                with TemporaryDirectory() as tmp_dir:
                    cmd = ['sentinel2', 'create-item', granule_href, tmp_dir]
                    self.run_command(cmd)

                    jsons = [
                        p for p in os.listdir(tmp_dir) if p.endswith('.json')
                    ]
                    self.assertEqual(len(jsons), 2)

                    for fname in jsons:
                        item = pystac.read_file(os.path.join(tmp_dir, fname))

                        item.validate()
                        check_proj_bbox(item)
