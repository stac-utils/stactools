import os.path

import boto3
from ftplib import FTP

from stactools.threedep.constants import USGS_FTP_SERVER, AWS_BUCKET, AWS_PREFIX
from stactools.threedep import utils


def fetch_ids(product: str, use_usgs_ftp: bool = False) -> [str]:
    """Returns all ids for the given product."""
    if use_usgs_ftp:
        return _fetch_ids_from_usgs_ftp(product)
    else:
        return _fetch_ids_from_aws(product)


def _fetch_ids_from_usgs_ftp(product: str) -> [str]:
    directory = f"vdelivery/Datasets/Staged/Elevation/{product}/TIFF"
    ftp = FTP(USGS_FTP_SERVER)
    ftp.login()
    ids = [
        file_name for (file_name, _) in ftp.mlsd(directory)
        if not file_name.startswith(".")
    ]
    ftp.close()
    return ids


def _fetch_ids_from_aws(product: str) -> [str]:
    path = os.path.dirname(utils.path(product, ""))
    prefix = os.path.join(AWS_PREFIX, path)
    client = boto3.client("s3")
    paginator = client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=AWS_BUCKET, Prefix=prefix)
    filtered_iterator = page_iterator.search(
        "Contents[?ends_with(Key, `.xml`)].Key")
    # The main tif/xml files for each id are named simply like "USGS_1_n41w106.tif".
    # If there's been updates, older versions will have a datetime on the end, e.g.
    # "USGS_1_n41w106_20210330.tif" or something similar. By splitting on underscores,
    # we're hoping to catch only the "main" files.
    return [
        os.path.basename(os.path.dirname(key)) for key in filtered_iterator
        if len(os.path.basename(key).split("_")) == 3
    ]


def path(product: str,
         id: str,
         base: str = None,
         extension: str = None,
         id_only: bool = False) -> str:
    """Returns the subpath for this product and id.

    E.g. path("1", "n41w106") == "1/TIFF/n41w106/USGS_1_n41w106"
    E.g. path("1", "n41w106", extension="tif") == "1/TIFF/n41w106/USGS_1_n41w106.tif"
    E.g. path("1", "n41w106", base="/base/dir") == "/base/dir/1/TIFF/n41w106/USGS_1_n41w106"
    E.g. path("1", "n41w106", id_only=True) == "/base/dir/1/TIFF/n41w106/n41w106"
    """
    if id_only:
        path = "{}/TIFF/{}/{}".format(product, id, id)
    else:
        path = "{}/TIFF/{}/USGS_{}_{}".format(product, id, product, id)
    if extension:
        path = "{}.{}".format(path, extension)
    if base:
        path = os.path.join(base, path)
    return path
