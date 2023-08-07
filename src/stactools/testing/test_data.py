import os
import shutil
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from typing import Any, Dict, Optional, Union
from zipfile import ZipFile

import fsspec
import requests


@dataclass
class ExternalData:
    """External data configurations for fetching and storing remote files.

    Args:
        url (str): URL at which the external data is found.
        compress (str): Compression method that has been used on external data.
            If provided, data is extracted after it is fetched.
            Only zip is supported. Defaults to None.
        s3 (Dict[str, Any]): Dictionary containing keyword arguments to use
            when instantiating ``s3fs.S3FileSystem``. Defaults to None.
        planetary_computer (bool): Whether external data is on planetary computer
            and needs to be signed. Defaults to False.

    """

    url: str
    compress: Optional[str] = None
    s3: Optional[Dict[str, Any]] = None
    planetary_computer: bool = False


@dataclass
class TestData:
    """A structure for getting paths to test data files, and fetching external
    data for local testing.

    Initializing this from, e.g., ``/home/user/my-package/tests/__init__.py``:

    .. code-block:: python

        test_data = TestData(__file__)

    Means that ``get_path`` will be relative to ``/home/user/my-package/tests``.

    .. code-block:: python

        test_data.get_path("data-files/basic")
        # "/home/user/my-package/tests/data-files/basic"

    When caching external data that base path is appended with
    ``test_data.external_subpath``  which by default is 'data-files/external'.

    For instance with the following external data configuration the external
    data file will be fetched from the URL, extracted from its zip file and
    locally stored at:
    ``/home/user/my-package/tests/data-files/external/AST_L1T_00305032000040446_20150409135350_78838.hdf``

    .. code-block:: python

        test_data.external_data = {
            'AST_L1T_00305032000040446_20150409135350_78838.hdf': {
                'url':
                    ('https://ai4epublictestdata.blob.core.windows.net/'
                    'stactools/aster/AST_L1T_00305032000040446_20150409135350_78838.zip'),
                'compress': 'zip'
            }
        }
        test_data.get_external_data("AST_L1T_00305032000040446_20150409135350_78838.hdf")

    Args:
        path (str): The path to any file in the directory where data is
            (or will be) stored. The directory information is taken from this
            path and used as the base for relative paths for the local data. It
            is stored on the class as ``self.base_path``
        external_data (Dict[str, ExternalData]):
            External data configurations for fetching and storing remote files.
            This is defined as a dictionary with the following structure: the
            key is the relative path (relative to
            ``self.base_path / self.external_subpath``) for cached data
            after it is fetched from remote and the value is the configuration
            as defined in :class:`ExternalData`.
        external_subpath (str): The subpath under ``self.base_path`` that is
            used for storing external data files. Defaults to 'data-files/external'
    """

    __test__ = False

    def __init__(
        self,
        path: str,
        external_data: Dict[str, Union[Dict[str, Any], ExternalData]] = {},
        external_subpath: str = "data-files/external",
    ) -> None:
        self.base_path = os.path.abspath(os.path.dirname(path))
        self.external_subpath = external_subpath
        self.external_data = external_data

    def get_path(self, rel_path: str) -> str:
        """Returns an absolute path to a local data file.

        Args:
            rel_path (str):
                The relative path to the test data file. The path is
                assumed to be relative to ``self.base_path``.

        Returns:
            str: The absolute path joining ``self.base_path`` and ``rel_path``
        """
        return os.path.join(self.base_path, rel_path)

    def get_external_data(self, rel_path: str) -> str:
        """Returns the path to the local cached version of the external data.

        If data is not yet cached, this method fetches it, caches it, then returns
        the path to the local cached version.

        Args:
            rel_path (str): This is both the filename that the local data will be
                stored at _and_ a key in the ``external_data`` dictionary where the
                corresponding value is the configuration information for the external
                data.

        Returns:
            str: The absolute path to the local cached version of the
                external data file.
        """
        path = self.get_path(os.path.join(self.external_subpath, rel_path))
        if not os.path.exists(path):
            config = self.external_data.get(rel_path)
            if config is None:
                raise Exception(
                    f"Local path {path} does not exist and there is no key "
                    f"in ``external_data`` that matches {rel_path}"
                )

            print(f"Downloading external test data {rel_path}...")
            os.makedirs(os.path.dirname(path), exist_ok=True)

            if not isinstance(config, ExternalData):
                config = ExternalData(**config)

            if config.s3:
                try:
                    import s3fs
                except ImportError as e:
                    print(
                        "Trying to download external test data via s3, "
                        "but s3fs is not installed and the download requires "
                        "configuring the s3fs filesystem. Install stactools "
                        "with s3fs via `pip install stactools[s3]` and try again."
                    )
                    raise (e)
                s3 = s3fs.S3FileSystem(**config.s3)
                with s3.open(config.url) as f:
                    data = f.read()
            elif config.planetary_computer:
                href = config.url
                r = requests.get(
                    "https://planetarycomputer.microsoft.com/api/sas/v1/sign?"
                    f"href={href}"
                )
                r.raise_for_status()
                signed_href = r.json()["href"]

                with fsspec.open(signed_href) as f:
                    data = f.read()

            else:
                with fsspec.open(config.url) as f:
                    data = f.read()

            if config.compress == "zip":
                with TemporaryDirectory() as tmp_dir:
                    tmp_path = os.path.join(tmp_dir, "file.zip")
                    with open(tmp_path, "wb") as f:
                        f.write(data)
                    z = ZipFile(tmp_path)
                    name = z.namelist()[0]
                    extracted_path = z.extract(name)
                    shutil.move(extracted_path, path)
            else:
                with open(path, "wb") as f:
                    f.write(data)

        return path
