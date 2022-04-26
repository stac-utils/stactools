.. _cli:
.. highlight:: shell


Command line interface (CLI)
============================

``stactools`` installs :program:`stac` as a command-line entrypoint.
To display all the available commands::

    $ stac --help

`stactools-packages <https://github.com/stactools-packages>`_ can extend the command line interface with their own commands via a plugin mechanism.
For example, you can browse a STAC catalog via a local server running `stac-browser <https://github.com/radiantearth/stac-browser>`_ via::

    $ pip install stactools-browse
    $ stac browse catalog.json

See specific ``stactools-package`` documentation for information about what
commands are available.

.. note::

    If you've installed ``stactools`` with AWS S3 support via ``pip install 'stactools[s3]'``, you can enable requester pays via::

        $ AWS_REQUEST_PAYER='requester' stac copy # ...etc...

Full documentation
------------------

.. click:: stactools.cli.cli:cli
   :prog: stac
   :nested: full
