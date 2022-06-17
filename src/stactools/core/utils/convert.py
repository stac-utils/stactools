"""Format conversion utilities."""

import os
from typing import Any, Dict, List, Optional, Tuple, cast

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


def check_gdal_driver() -> None:
    if not utils.gdal_driver_is_enabled("COG"):
        raise DriverRegistrationError(
            "GDAL's COG driver is not enabled, make sure you're using GDAL >= 3.1"
        )


def cogify(
    infile: str,
    outfile: str,
    band: Optional[int] = None,
    profile: Optional[Dict[str, Any]] = None,
) -> None:
    """Creates a Cloud-Optimized GeoTIFF (COG) from a GDAL-readable file
    without subdatasets (non-HDF files). A band number can optionally be
    provided to extract a single band from a multiband file.

    Uses :py:meth:`rasterio.shutil.copy`.

    Args:
        infile (str): The input file.
        outfile (str): The output COG to be written.
        band (Optional[int]): The band number in the input file to extract.
        profile (Optional[dict[str, Any]]):
            An optional profile to use on the
            output file. If not provided,
            :py:const:`stactools.core.utils.convert.DEFAULT_PROFILE` will be
            used.
    """
    check_gdal_driver()

    src = rasterio.open(infile)
    dest_profile = DEFAULT_PROFILE.copy()
    dest_profile.update(
        {
            "dtype": rasterio.uint8,
            "width": src.width,
            "height": src.height,
            "crs": src.crs,
            "transform": src.transform,
        }
    )

    if profile:
        dest_profile.update(profile)

    # If a band number was provided, create a single-band COG
    if band:
        single_band = src.read(band)
        dest_profile.update({"count": 1})
        with rasterio.open(outfile, "w", **dest_profile) as dest:
            dest.write(single_band, 1)
    # If no band numbers were provided, create a multi-band COG
    else:
        dest_profile.update({"count": src.count})
        rasterio.shutil.copy(infile, outfile, **dest_profile)


def cogify_subdataset(infile: str, outfile: str) -> None:
    """Exports a Cloud-Optimized GeoTIFF (COG) from a subdataset within an HDF file.
    Uses :py:meth:`rasterio.shutil.copy`.
    Args:
        infile (str): The input file.
        outfile (str): The output COG to be written.
    """
    check_gdal_driver()
    destination_profile = DEFAULT_PROFILE.copy()
    rasterio.shutil.copy(infile, outfile, **destination_profile)


def list_subdataset(infile: str, outdir: str) -> Tuple[List[str], List[str]]:
    """Generates lists of output paths and subdataset names for COGs created from an HDF file.
    This is then used to call the cogify_subdataset() function to export out COG files.
    Args:
        infile (str): The input HDF file
        outdir (str): The output directory where the HDF files will be created
    Returns:
        Tuple[List[str], List[str]]: A two tuple (paths, names):
            - The first element is a list of the output tiff paths
            - The second element is a list of subdataset names
    """

    with rasterio.open(infile) as dataset:
        subdatasets = cast(List[str], dataset.subdatasets)
        base_file_name = os.path.splitext(os.path.basename(infile))[0]
        paths = []
        subdataset_names = []
        for subdataset in subdatasets:
            parts = subdataset.split(":")
            subdataset_name = parts[-1]
            sanitized_subdataset_name = subdataset_name.replace(" ", "_").replace(
                "/", "_"
            )
            subdataset_names.append(sanitized_subdataset_name)
            file_name = f"{base_file_name}_{sanitized_subdataset_name}.tif"
            outfile = os.path.join(outdir, file_name)
            cogify_subdataset(subdataset, outfile)
            paths.append(outfile)
        return (paths, subdataset_names)
