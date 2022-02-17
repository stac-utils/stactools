from typing import Dict, Any, Optional

import rasterio
import rasterio.shutil
from rasterio.errors import DriverRegistrationError

from stactools.core import utils

DEFAULT_PROFILE = {
    "compress": "deflate",
    "driver": "COG",
    "blocksize": 512,
}


def cogify(infile: str,
           outfile: str,
           profile: Optional[Dict[str, Any]] = None) -> None:
    """Creates a COG from a GDAL-readable file."""
    if not utils.gdal_driver_is_enabled("COG"):
        raise DriverRegistrationError(
            "GDAL's COG driver is not enabled, make sure you're using GDAL >= 3.1"
        )
    destination_profile = DEFAULT_PROFILE.copy()
    if profile:
        destination_profile.update(profile)
    rasterio.shutil.copy(infile, outfile, **destination_profile)
