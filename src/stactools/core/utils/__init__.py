"""General utility functions."""

import warnings
from contextlib import contextmanager
from typing import Callable, Generator, Optional, TypeVar

import fsspec
import pystac.utils
import rasterio
from rasterio.errors import NotGeoreferencedWarning

T = TypeVar("T")
U = TypeVar("U")


def map_opt(fn: Callable[[T], U], v: Optional[T]) -> Optional[U]:
    """DEPRECATED: use :py:meth:`pystac.utils.map_opt` instead."""
    deprecate("stactools.core.utils.map_opt", "pystac.utils.map_opt", "v0.5.0")
    return pystac.utils.map_opt(fn, v)


def href_exists(href: str) -> bool:
    """Returns true if there is a file at the given href.

    Uses fssepc and its `exists
    <https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.spec.AbstractFileSystem.exists>`_
    method.

    Args:
        href (str): The href to check.

    Returns:
        bool: True if the href exists, False if not.
    """
    fs, _, paths = fsspec.get_fs_token_paths(href)
    return bool(paths and fs.exists(paths[0]))


def gdal_driver_is_enabled(name: str) -> bool:
    """Checks to see if the named GDAL driver is enabled.

    Checks for the name in :py:meth:`rasterio.Env.drivers`.

    Args:
        name (str): The name of the driver.

    Returns:
        bool: True if the driver is enabled, False otherwise.
    """
    with rasterio.Env() as env:
        return name in env.drivers().keys()


def deprecate(from_: str, to: str, version: str) -> None:
    r"""Warn with :py:class:`DeprecationWarning` and a pre-canned message.

    The message is something like:

        Foo is deprecated and will be removed in v0.42.0. Use Bar instead.

    Args:
        from\_ (str): The current function/method/class name.
        to (str): The name that should be used instead.
        version (str): The version at which the function/method/class will be removed.
    """
    warnings.warn(
        f"{from_} is deprecated and will be removed in {version}. Use {to} instead.",
        DeprecationWarning,
        stacklevel=2,
    )


@contextmanager
def ignore_not_georeferenced() -> Generator[None, None, None]:
    """Suppress rasterio's warning when opening a dataset that contains no
    georeferencing information."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=NotGeoreferencedWarning)
        yield
