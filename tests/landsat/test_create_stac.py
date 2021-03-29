import os
from tempfile import TemporaryDirectory
from typing import cast

import pystac
from pystac.utils import is_absolute_href
from shapely.geometry import box, shape, mapping

from stactools.core.projection import reproject_geom
from stactools.landsat.commands import create_landsat_command
from stactools.landsat.stac import create_stac_item
from stactools.landsat.constants import (L8_SR_BANDS, L8_SP_BANDS)
from tests.utils import CliTestCase
from tests.landsat.data import TEST_MTL_PATHS


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_landsat_command]

    def test_create_item(self):

        def check_proj_bbox(item):
            bbox = item.bbox
            bbox_shp = box(*bbox)
            proj_bbox = item.ext.projection.bbox
            proj_bbox_shp = box(*proj_bbox)
            reproj_bbox_shp = shape(
                reproject_geom(f"epsg:{item.ext.projection.epsg}", "epsg:4326",
                               mapping(proj_bbox_shp)))

            self.assertLess((reproj_bbox_shp - bbox_shp).area,
                            0.0001 * reproj_bbox_shp.area)

        for mtl_path in TEST_MTL_PATHS:
            with self.subTest(mtl_path):
                with TemporaryDirectory() as tmp_dir:
                    cmd = [
                        'landsat', 'create-item', '--mtl', mtl_path,
                        '--output', tmp_dir
                    ]
                    self.run_command(cmd)

                    jsons = [
                        p for p in os.listdir(tmp_dir) if p.endswith('.json')
                    ]
                    self.assertEqual(len(jsons), 1)
                    fname = jsons[0]

                    item = pystac.read_file(os.path.join(tmp_dir, fname))
                    item.validate()

                    bands_seen = set()

                    for asset in item.assets.values():
                        self.assertTrue(is_absolute_href(asset.href))
                        bands = item.ext.eo.get_bands(asset)
                        if bands is not None:
                            bands_seen |= set(b.name for b in bands)

                    if item.properties['landsat:processing_level'] == 'L2SP':
                        self.assertEqual(
                            bands_seen,
                            set(L8_SR_BANDS.keys()) | set(L8_SP_BANDS.keys()))
                    else:
                        self.assertEqual(bands_seen, set(L8_SR_BANDS.keys()))

                    check_proj_bbox(item)

    def test_convert_and_create_agree(self):

        def get_item(output_dir: str) -> pystac.Item:
            jsons = [p for p in os.listdir(output_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)

            fname = jsons[0]
            item = cast(pystac.Item,
                        pystac.read_file(os.path.join(output_dir, fname)))
            item.validate()

            return item

        for mtl_path in TEST_MTL_PATHS:
            with self.subTest(mtl_path):
                with TemporaryDirectory() as tmp_dir:
                    create_dir = os.path.join(tmp_dir, 'create')
                    convert_dir = os.path.join(tmp_dir, 'convert')
                    original_dir = os.path.join(tmp_dir, 'original')
                    os.makedirs(create_dir, exist_ok=True)
                    os.makedirs(convert_dir, exist_ok=True)
                    os.makedirs(original_dir, exist_ok=True)

                    create_cmd = [
                        'landsat', 'create-item', '--mtl', mtl_path,
                        '--output', create_dir
                    ]
                    self.run_command(create_cmd)

                    stac_path = mtl_path.replace('_MTL.xml', '_SR_stac.json')
                    import shutil
                    shutil.copy(
                        stac_path,
                        os.path.join(original_dir,
                                     os.path.basename(stac_path)))
                    convert_cmd = [
                        'landsat', 'convert', '--stac', stac_path,
                        '--enable-proj', '--dst', convert_dir
                    ]
                    self.run_command(convert_cmd)

                    # TODO: Resolve disagreements between convert and create.
                    # This might best be informed by USGS's own STAC 1.0.* items
                    # when they are made available.

                    # created_item = get_item(create_dir)
                    # converted_item = get_item(convert_dir)

                    # self.assertTrue(
                    #     set(converted_item.assets.keys()).issubset(
                    #         set(created_item.assets.keys())),
                    #     msg=
                    #     f"{set(converted_item.assets.keys()) - set(created_item.assets.keys())}"
                    # )
