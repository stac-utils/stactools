API Reference
=============

This API reference is auto-generated for the Python docstrings.

Core
----

The ``stactools.core`` package contains utility methods for dealing with STACs.

Functions are organized into subpackages but can be imported directly from ``stactools.core``, e.g.:

.. code-block:: python

   from stactools.core import (copy_catalog, merge_catalogs)

Copying and Moving
~~~~~~~~~~~~~~~~~~

.. autofunction:: stactools.core.copy.copy_catalog

.. autofunction:: stactools.core.copy.move_all_assets

.. autofunction:: stactools.core.copy.move_assets

.. autofunction:: stactools.core.copy.move_asset_file_to_item

Merging
~~~~~~~

.. autofunction:: stactools.core.merge.merge_all_items

.. autofunction:: stactools.core.merge.merge_items

Layout
~~~~~~

.. autofunction:: stactools.core.layout.layout_catalog
