``stactools`` Documentation
###########################

``stactools`` is a library for working with `SpatioTemporal Asset Catalogs (STAC) <https://stacspec.org/>`_ based on `PySTAC <https://github.com/stac-utils/pystac>`_.

``stactools`` provides a CLI via the ``stac`` command:

.. code-block:: console

   > stac --help

Requirements
============
* `Python 3 <https://www.python.org/>`_

STAC Versions
=============

* 0.1 -> STAC Version 1.0

Standard pip install
====================

.. code-block:: console

   pip install stactools

Core subpackages are available from PyPI:

.. code-block:: console

   pip install stactools-planet

``stactools`` Features
======================

Use ``stac --help`` to navigate the varios commands.

* ``stac copy`` copies STACs and optionally assets
* ``stac info`` and ``stac describe`` display information about STACs
* ``stac layout`` will modify the layout of a STAC based on item properties

One of the focuses of ``stactools`` is to provide an easy way to plug in functionality for different data sources. For example:

* ``stac planet convert-order`` will convert a Planet order into a STAC.

See the :ref:`cli` documentation for more details about each command.

Table of Contents
=================

.. toctree::
   :maxdepth: 2

   api
   cli