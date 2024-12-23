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


def assert_cog_driver_is_enabled() -> None:
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
    """Creates a Cloud-Optimized GeoTIFF (COG) from a GDAL-readable file.

    A band number can optionally be provided to extract a single band from a
    multiband file. To create COGs from subdatasets, use
    :py:meth:`stactools.core.utils.convert.cogify_subdatasets`.

    Args:
        infile (str): The input file.
        outfile (str): The output COG to be written.
        band (Optional[int]): The band number in the input file to extract.
                            If not provided, a multi-band COG will be created.
        profile (Optional[dict[str, Any]]):
            An optional profile to use on the
            output file. If not provided,
            :py:const:`stactools.core.utils.convert.DEFAULT_PROFILE` will be
            used.
    """
    assert_cog_driver_is_enabled()

    src = rasterio.open(infile)
    dest_profile = DEFAULT_PROFILE.copy()
    dest_profile.update(
        {
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
        dest_profile.update({"count": 1, "dtype": single_band.dtype})
        with rasterio.open(outfile, "w", **dest_profile) as dest:
            dest.write(single_band, 1)
    # If no band numbers were provided, create a multi-band COG
    else:
        dest_profile.update({"count": src.count, "dtype": src.dtypes[0]})
        rasterio.shutil.copy(infile, outfile, **dest_profile)


def cogify_subdatasets(
    infile: str, outdir: str, subdataset_names: Optional[List[str]] = None
) -> Tuple[List[str], List[str]]:
    """Creates Cloud-Optimized GeoTIFFs for all subdatasets in a multi-dataset
    raster file.

    The created files will be named the same as the source file, with a
    ``_SUBDATASET`` suffix.  E.g. if the source file is named ``foo.hdf`` and
    the subdataset is named ``bar``, the output COG will be named
    ``foo_bar.tif``. Only 2D (and not 3D) subdatasets are supported.

    Args:
         infile (str): The input file containing subdatasets.
         outdir (str): The output directory where the COGs will be created.
    Returns:
         Tuple[List[str], List[str]]:
             A two tuple (paths, names):
                 - The first element is a list of the output COG paths
                 - The second element is a list of subdataset names
    """

    assert_cog_driver_is_enabled()
    with rasterio.open(infile) as dataset:
        subdatasets = cast(List[str], dataset.subdatasets)
        base_file_name = os.path.splitext(os.path.basename(infile))[0]
        paths = []
        names = []
        for subdataset in subdatasets:
            with rasterio.open(subdataset) as subd:
                if len(subd.shape) != 2:
                    continue
                parts = subdataset.split(":")
                subdataset_name = parts[-1]
                if subdataset_names and subdataset_name not in subdataset_names:
                    continue
                sanitized_subdataset_name = (
                    subdataset_name.strip()
                    .strip("/")
                    .replace(" ", "_")
                    .replace("/", "_")
                )
                names.append(sanitized_subdataset_name)
                file_name = f"{base_file_name}_{sanitized_subdataset_name}.tif"
                outfile = os.path.join(outdir, file_name)
                destination_profile = DEFAULT_PROFILE.copy()
                rasterio.shutil.copy(subdataset, outfile, **destination_profile)
                paths.append(outfile)
        return (paths, names)
