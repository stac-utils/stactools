"""Format conversion utilities."""

from typing import Any, Dict, Optional

import rasterio
import rasterio.shutil
from rasterio.errors import DriverRegistrationError

from stactools.core import utils

DEFAULT_PROFILE = {
    "compress": "deflate",
    "driver": "COG",
    "blocksize": 512,
}
"""The default profile to use when writing Cloud-Optimized GeoTIFFs (COGs)."""


def cogify(infile: str, outfile: str, profile: Optional[Dict[str, Any]] = None) -> None:
    """Creates a Cloud-Optimized GeoTIFF (COG) from a GDAL-readable file.

    Uses :py:meth:`rasterio.shutil.copy`.

    Args:
        infile (str): The input file.
        outfile (str): The output COG to be written.
        profile (Optional[dict[str, Any]]):
            An optional profile to use on the
            output file. If not provided,
            :py:const:`stactools.core.utils.convert.DEFAULT_PROFILE` will be
            used.
    """
    if not utils.gdal_driver_is_enabled("COG"):
        raise DriverRegistrationError(
            "GDAL's COG driver is not enabled, make sure you're using GDAL >= 3.1"
        )
    destination_profile = DEFAULT_PROFILE.copy()
    if profile:
        destination_profile.update(profile)
    rasterio.shutil.copy(infile, outfile, **destination_profile)
