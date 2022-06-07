import os
import shutil
from tempfile import TemporaryDirectory


def create_temp_copy(
    src_path: str, tmp_dir: TemporaryDirectory, target_name: str
) -> str:
    """Create a temporary copy of a file

    Args:
        src_path (str): path of the file to be copied.
        tmp_dir (TemporaryDirectory): path of the temporary directory where the file will be copied.
        target_name (str): name of the file in the target location.

    Returns:
        str: path of the temporary copy of the file.
    """
    temp_path = os.path.join(tmp_dir, target_name)
    shutil.copyfile(src_path, temp_path)
    return temp_path
