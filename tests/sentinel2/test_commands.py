from collections import defaultdict
import os
from tempfile import TemporaryDirectory

import pystac
from pystac.extensions.eo import EOExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.utils import is_absolute_href
from shapely.geometry import box, shape, mapping

from stactools.core.projection import reproject_geom
from stactools.sentinel2.commands import create_sentinel2_command
from stactools.sentinel2.constants import BANDS_TO_RESOLUTIONS, SENTINEL_BANDS
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
                box(*ProjectionExtension.ext(item.assets["visual-10m"]).bbox))
            proj_geom = shape(
                reproject_geom(f'epsg:{ProjectionExtension.ext(item).epsg}',
                               'epsg:4326', pb))

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
                    self.assertEqual(len(jsons), 1)
                    fname = jsons[0]

                    item = pystac.read_file(os.path.join(tmp_dir, fname))

                    item.validate()

                    import json
                    with open('s2-item.py', 'w') as f:
                        json.dump(item.to_dict(), f, indent=2)

                    bands_seen = set()
                    bands_to_assets = defaultdict(list)

                    for key, asset in item.assets.items():
                        self.assertTrue(is_absolute_href(asset.href))
                        bands = EOExtension.ext(asset).bands
                        if bands is not None:
                            bands_seen |= set(b.name for b in bands)
                            if key.split('_')[0] in SENTINEL_BANDS:
                                for b in bands:
                                    bands_to_assets[b.name].append(
                                        (key, asset))

                    self.assertEqual(bands_seen, set(SENTINEL_BANDS.keys()))

                    # Check that multiple resolutions exist for assets that
                    # have them, and that they are named such that the highest
                    # resolution asset is the band name, and others are
                    # appended with the resolution.

                    resolutions_seen = defaultdict(list)

                    for band_name, assets in bands_to_assets.items():
                        for (asset_key, asset) in assets:
                            resolutions = BANDS_TO_RESOLUTIONS[band_name]

                            asset_split = asset_key.split('_')
                            self.assertLessEqual(len(asset_split), 2)

                            href_band, href_res = os.path.splitext(
                                asset.href)[0].split('_')[-2:]
                            asset_res = int(href_res.replace('m', ''))
                            self.assertEqual(href_band, band_name)
                            if len(asset_split) == 1:
                                self.assertEqual(asset_res, resolutions[0])
                                self.assertIn('gsd', asset.properties)
                                resolutions_seen[band_name].append(asset_res)
                            else:
                                self.assertNotEqual(asset_res, resolutions[0])
                                self.assertIn(asset_res, resolutions)
                                self.assertNotIn('gsd', asset.properties)
                                resolutions_seen[band_name].append(asset_res)

                    self.assertEqual(set(resolutions_seen.keys()),
                                     set(BANDS_TO_RESOLUTIONS.keys()))
                    for band in resolutions_seen:
                        self.assertEqual(set(resolutions_seen[band]),
                                         set(BANDS_TO_RESOLUTIONS[band]))

                    check_proj_bbox(item)
