``stactools`` documentation
###########################

``stactools`` is a library for working with `SpatioTemporal Asset Catalogs (STAC) <https://stacspec.org/>`_.
It is based on `PySTAC <https://github.com/stac-utils/pystac>`_.
The ``stactools`` package provides:

- A core Python API, available via :py:mod:`stactools.core`, which provides
  high-level utility functions for working with STAC objects
- A command-line interface, available via the ``stac`` command, e.g.:

.. code-block:: shell

   $ stac --help

There are a variety of ``stactools`` packages built for specific datasets or to provide extra functionality.
See the `stactools-packages website <https://stactools-packages.github.io>`_ and the `stactools-packages Github organization <https://github.com/stactools-packages>`_ for more information.

Requirements
============

* `Python 3.7 or greater <https://www.python.org/>`_

STAC version support
====================

All versions of ``stactools`` support STAC v1.0.0.

Installation
============

.. code-block:: shell

   $ pip install stactools

Filesystem I/O is provided by `fsspec <https://filesystem-spec.readthedocs.io/en/latest/>`_.
To enable AWS S3 support via `s3fs <https://github.com/fsspec/s3fs>`_, you can enable it during installation.

.. code-block:: shell

    $ pip install 'stactools[s3]'

.. note::

    If you need to access s3 data via requester pays, use this environment variable: ``AWS_REQUEST_PAYER='requester'``.

More information
================

.. toctree::
   :maxdepth: 1

   cli
   api
   builder
