from typing import List, Optional

from stactools.core.utils.subprocess import call

DEFAULT_COGIFY_ARGS = ["-co", "compress=deflate"]


def cogify(infile: str,
           outfile: str,
           args: Optional[List[str]] = None,
           extra_args: Optional[List[str]] = None) -> int:
    """Creates a COG from a GDAL-readable file."""
    if args is None:
        args = DEFAULT_COGIFY_ARGS[:]
    args = ["gdal_translate", "-of", "COG"] + args
    if extra_args:
        args.extend(extra_args)
    args.append(infile)
    args.append(outfile)
    return call(args)
