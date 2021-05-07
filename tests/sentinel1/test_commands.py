import os
from tempfile import TemporaryDirectory

import pystac
from pystac.utils import is_absolute_href

from stactools.sentinel1.commands import create_sentinel1_command

from tests.utils import (TestData, CliTestCase)


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_sentinel1_command]

    def test_create_item(self):
        granule_hrefs = [
            TestData.get_path(f'data-files/sentinel1/{x}') for x in [
                'S1B_20161121_12SYJ_ASC',
            ]
        ]

        for granule_href in granule_hrefs:
            with self.subTest(granule_href):
                with TemporaryDirectory() as tmp_dir:
                    cmd = [
                        'sentinel1', 'create-item', granule_href, tmp_dir,
                        '-a', 'local_incident_angle.vrt'
                    ]
                    self.run_command(cmd)

                    jsons = [
                        p for p in os.listdir(tmp_dir) if p.endswith('.json')
                    ]
                    self.assertEqual(len(jsons), 1)

                    for fname in jsons:
                        item = pystac.read_file(os.path.join(tmp_dir, fname))

                        item.validate()

                        for asset in item.assets.values():
                            self.assertTrue(is_absolute_href(asset.href))
