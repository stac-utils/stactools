## stactools
![Build Status](https://github.com/stac-utils/stactools/workflows/CI/badge.svg)
[![Documentation](https://readthedocs.org/projects/stactools/badge/?version=latest)](https://stactools.readthedocs.io/en/latest/)
[![PyPI version](https://img.shields.io/pypi/v/stactools)](https://pypi.org/project/stactools/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

`stactools` is a command line tool and library for working with [STAC](https://stacspec.org).
It is based on [PySTAC](https://github.com/stac-utils/pystac).

This is the core `stactools` repository, which provides a basic command line interface (CLI) and API for working with STAC catalogs.
There are a suite of packages available in other repositories for working with a variety of datasets and for doing more complicated oprations on STAC data.
See [packages](#packages) for more information.

## Installation

To install the latest stable version:

```bash
> pip install stactools
```

From source repository:

```bash
> git clone https://github.com/stac-utils/stactools.git
> cd stactools
> pip install .
```

**NOTE:** In order to read and write Cloud Optimized Geotiffs, GDAL version 3.1 or greater is required.
If your system GDAL is older than version 3.1, consider using [Docker](#using-docker) or [Conda](#using-conda) to get a modern GDAL.

### Optional dependencies

`stactools` includes some optional dependencies:
- `s3`: Enables s3 hrefs via `fsspec` and `s3fs`

To install a single optional dependency:

```bash
> pip install stactools[s3]
```

To install all optional dependencies:

```bash
> pip install stactools[all]
```

### Docker

To download the Docker image from the registry:

```bash
> docker pull ghcr.io/stac-utils/stactools:latest
```

## Running

```bash
> stac --help
```

### Docker

```bash
> docker run --rm ghcr.io/stac-utils/stactools:latest --help
```

## Documentation

See the [documentation page](https://stactools.readthedocs.io/en/latest/) for the latest docs.

## Packages

`stactools` is comprised of many other sub-packages that provide library and CLI functionality.
Officially supported packages are hosted in the Github `stactools-packages` organization, and other subpackages may be available from other sources.
Below is a list of officially supported packages and their current build status.
Each package can be installed via `pip install stactools-{package}`, e.g. `pip install stactools-landsat`.
Third-party packages can be installed in the same way, or, if they are not on PyPI, directly from the source repository, e.g. `pip install /path/to/my/code/stactools-greatdata`.

### Function packages

These extend the `stac` command line utility to provide additional funcionality.

| name                                                                       | description                                                                                 | build status                                                                                                                                                                                                                |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [stactools-browse](https://github.com/stactools-packages/stactools-browse) | Launch [stac-browser](https://github.com/radiantearth/stac-browser) against a local catalog | [![CI](https://github.com/stactools-packages/stactools-browse/actions/workflows/continuous-integration.yml/badge.svg)](https://github.com/stactools-packages/stactools-browse/actions/workflows/continuous-integration.yml) |

### Dataset packages

These are designed to work with specific types of geospatial data.

| name                                                                               | data type                                                                  | build status                                                                                                                                                                                                                        |
| ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [stactools-aster](https://github.com/stactools-packages/stactools-aster)           | ASTER                                                                      |                                                                                                                                                                                                                                     |
| [stactools-cgls_lc100](https://github.com/stactools-packages/stactools-cgls_lc100) | Copernicus Global Land Cover Layers                                        | [![CI](https://github.com/stactools-packages/stactools-cgls_lc100/actions/workflows/continuous-integration.yml/badge.svg)](https://github.com/stactools-packages/stactools-cgls_lc100/actions/workflows/continuous-integration.yml) |
| [stactools-corine](https://github.com/stactools-packages/stactools-corine)         | CORINE Land Cover                                                          | [![CI](https://github.com/stactools-packages/stactools-corine/actions/workflows/continuous-integration.yml/badge.svg)](https://github.com/stactools-packages/stactools-corine/actions/workflows/continuous-integration.yml)         |
| [stactools-landsat](https://github.com/stactools-packages/stactools-landsat)       | USGS LANDSAT                                                               | [![CI](https://github.com/stactools-packages/stactools-landsat/actions/workflows/continuous-integration.yml/badge.svg)](https://github.com/stactools-packages/stactools-landsat/actions/workflows/continuous-integration.yml)       |
| [stactools-naip](https://github.com/stactools-packages/stactools-naip)             | USDA National Agriculture Imagery Program                                  | [![CI](https://github.com/stactools-packages/stactools-naip/actions/workflows/continuous-integration.yml/badge.svg)](https://github.com/stactools-packages/stactools-naip/actions/workflows/continuous-integration.yml)             |
| [stactools-planet](https://github.com/stactools-packages/stactools-planet)         | Planet                                                                     | [![CI](https://github.com/stactools-packages/stactools-planet/actions/workflows/continuous-integration.yml/badge.svg)](https://github.com/stactools-packages/stactools-planet/actions/workflows/continuous-integration.yml)         |
| [stactools-sentinel2](https://github.com/stactools-packages/stactools-sentinel2)   | Sentinel-2                                                                 | [![CI](https://github.com/stactools-packages/stactools-sentinel2/actions/workflows/continuous-integration.yml/badge.svg)](https://github.com/stactools-packages/stactools-sentinel2/actions/workflows/continuous-integration.yml)   |
| [stactools-threedep](https://github.com/stactools-packages/stactools-threedep)     | USGS 3D Elevation Program (formerly the National Elevation Dataset or NED) | [![CI](https://github.com/stactools-packages/stactools-threedep/actions/workflows/continuous-integration.yml/badge.svg)](https://github.com/stactools-packages/stactools-threedep/actions/workflows/continuous-integration.yml)     |

## Developing

Some packages require environments with more complex environments than can be set up just through pip.
For example, the `stactools.aster` package uses rasterio functionality that required a GDAL enabled with the HDF4 format.
Because of this, it's recommended to utilize docker or conda to ensure a consistent environment.

### Using docker

Build the container with:

```
> docker/build
```

Once the container is built, you can run the `scripts/` scripts inside a docker console by running:

```
> docker/console
```

A complete build and test can be run with:

```
> docker/cibuild
```

It is recommended to do a Docker CI build before submitting a pull request to ensure your changes will (likely) pass Github's CI.

In scenarios where you want to run scripts in `docker/` but don't want to run the build, images can be downloaded via the `pull` script:

```
> docker/pull
```

Run a Juypter notebook:

```
> docker/notebook
```

### Using conda

[conda](https://docs.conda.io/en/latest/) is a useful tool for managing dependencies, both binary and Python-based.
If you have conda installed, you can create a new environment for `stactools` development by running the following command from the top-level directory in this repo:

```
> conda env create -f environment.yml
```

Then activate the `stactools` environment:

```
> conda activate stactools
```

Finally, install `stactools` in editable mode and all development requirements:

```
> pip install -e .
> pip install -r requirements-dev.txt
```

### Using virtualenv

If not using docker or conda, it's recommended to use [virtualenv](https://virtualenv.pypa.io/en/latest/index.html) to keep isolate the python environment used to develop `stactools`.
See virtualenv documentation for more detailed information, but as a shortcut here's some quick steps:

- Make sure [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) is installed
- Run `virtualenv venv`
- Activate the virtualenv with `source venv/bin/activate`

### Running the CLI against development code

You can run the CLI through docker by running

```
> docker/stac --help
```

or in the local environment with

```
> scripts/stac --help
```

### Unit Tests

Unit tests are in the `tests` folder. To run unit tests, use `unittest`:

```
> python -m unittest discover tests
```

To run linters, code formatters, and test suites all together, use `test`:

```
> ./docker/test
```

or

```
> ./scripts/test
```

The test script also runs lint and code quality checks.

Run a Juypter notebook:

```
> scripts/notebook
```

### Documentation

To build and serve the docs, all of the requirements must be installed with `scripts/update`.
Make sure [Pandoc](https://pandoc.org/installing.html) is installed.
Also make sure sphinx is available, which should be installed with `requirements-dev.txt`.
You can also run the following in the docker container using

```
> docker/console
```

To build the docs, you can use `make html`, and to build the docs and start a server that watches for changes, use `make livehtml`:

```
> cd docs
> make html
> make livehtml
```

If using `make livehtml`, once the server starts, navigate to [http://localhost:8000](http://localhost:8000/) to see the docs.

Use 'make' without arguments to see a list of available commands.

### Adding a new package

To create a new `stactools` package, use the [`stactools` package template](https://github.com/stactools-packages/template).
`stactools` utilizes Python's [namespace packages](https://packaging.python.org/guides/packaging-namespace-packages/) to provide a suite of tools all under the `stactools` namespace.
If you would like your package to be considered for inclusion as a core `stactools` package, please open an issue on this repository with a link to your package repository.
