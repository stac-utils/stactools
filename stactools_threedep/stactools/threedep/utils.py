import os.path

from ftplib import FTP

from stactools.threedep.constants import USGS_FTP_SERVER


def fetch_ids(product: str) -> [str]:
    """Returns all ids for the given product."""
    directory = f"vdelivery/Datasets/Staged/Elevation/{product}/TIFF"
    ftp = FTP(USGS_FTP_SERVER)
    ftp.login()
    ids = [
        file_name for (file_name, _) in ftp.mlsd(directory)
        if not file_name.startswith(".")
    ]
    ftp.close()
    return ids


def path(product: str,
         id: str,
         extension: str = None,
         base: str = None) -> str:
    """Returns the subpath for this product and id.

    E.g. path("1", "n41w106") == "1/TIFF/n41w106/USGS_1_n41w106"
    E.g. path("1", "n41w106", extension="tif") == "1/TIFF/n41w106/USGS_1_n41w106.tif"
    E.g. path("1", "n41w106", base="/base/dir") == "/base/dir/1/TIFF/n41w106/USGS_1_n41w106"
    """
    path = "{}/TIFF/{}/USGS_{}_{}".format(product, id, product, id)
    if extension:
        path = "{}.{}".format(path, extension)
    if base:
        path = os.path.join(base, path)
    return path
