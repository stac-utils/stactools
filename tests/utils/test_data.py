import os
import shutil
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import requests

CLGS_LC100_DIR = 'record/3939050/files'
CLGS_LC100_TIF = 'PROBAV_LC100_global_v3.0.1_2019-nrt_Change-Confidence-layer_EPSG-4326.tif'
CLGS_LC100_PARAM = 'download=1'

EXTERNAL_DATA = {
    'aster/AST_L1T_00301012006003619_20150512141939_7778.hdf': {
        'url':
        ('https://ai4epublictestdata.blob.core.windows.net/'
         'stactools/aster/AST_L1T_00301012006003619_20150512141939_7778.zip'),
        'compress':
        'zip'
    },
    'cgls_lc100/PROBAV_LC100_global_v3.0.1_2019-nrt_ccl.tif': {
        'url': ('https://zenodo.org/'
                '{}/{}?{}'.format(CLGS_LC100_DIR, CLGS_LC100_TIF,
                                  CLGS_LC100_PARAM)),
        'compress':
        'none'
    }
}


class TestData:
    @staticmethod
    def get_path(rel_path):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', rel_path))

    @staticmethod
    def get_external_data(rel_path):
        path = TestData.get_path(os.path.join('data-files/external', rel_path))
        if not os.path.exists(path):
            entry = EXTERNAL_DATA.get(rel_path)
            if entry is None:
                raise Exception('Path {} does not exist and there is no entry '
                                'for external test data {}.'.format(
                                    path, rel_path))

            print('Downloading external test data {}...'.format(rel_path))
            os.makedirs(os.path.dirname(path), exist_ok=True)

            resp = requests.get(entry['url'])
            if entry['compress'] == 'zip':
                with TemporaryDirectory() as tmp_dir:
                    tmp_path = os.path.join(tmp_dir, 'file.zip')
                    with open(tmp_path, 'wb') as f:
                        f.write(resp.content)
                    z = ZipFile(tmp_path)
                    name = z.namelist()[0]
                    extracted_path = z.extract(name)
                    shutil.move(extracted_path, path)
            else:
                with open(path, 'wb') as f:
                    f.write(resp.content)

        return path
