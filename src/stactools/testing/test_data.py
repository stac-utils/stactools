import os
import shutil
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import requests

EXTERNAL_DATA = {
    'aster/AST_L1T_00305032000040446_20150409135350_78838.hdf': {
        'url':
        ('https://ai4epublictestdata.blob.core.windows.net/'
         'stactools/aster/AST_L1T_00305032000040446_20150409135350_78838.zip'),
        'compress':
        'zip'
    }
}


class TestData:
    def __init__(self, path):
        """Creates a test data object for a given test script.

        Initialize this from, e.g., `tests/__init__.py`:

        ```
        test_data = TestData(__file__)
        ```
        """
        self.path = path

    def get_path(self, rel_path: str) -> str:
        return os.path.abspath(
            os.path.join(os.path.dirname(self.path), rel_path))

    def get_external_data(self, rel_path: str) -> str:
        path = self.get_path(os.path.join('data-files/external', rel_path))
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
