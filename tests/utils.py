import os
import shutil

import pystac

from . import test_data


def create_temp_copy(src_path: str, tmp_dir: str, target_name: str) -> str:
    """Create a temporary copy of a file

    Args:
        src_path (str): path of the file to be copied.
        tmp_dir (TemporaryDirectory): path of the temporary directory where the
            file will be copied.
        target_name (str): name of the file in the target location.

    Returns:
        str: path of the temporary copy of the file.
    """
    temp_path = os.path.join(tmp_dir, target_name)
    shutil.copyfile(src_path, temp_path)
    return temp_path


def create_planet_disaster_clone(tmp_dir: str) -> pystac.Collection:
    src = test_data.get_path("data-files/planet-disaster")
    dst = os.path.join(tmp_dir, "planet-disaster")
    shutil.copytree(src, dst)

    return pystac.Collection.from_file(os.path.join(dst, "collection.json"))
