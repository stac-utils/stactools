# stactools

![Build Status](https://github.com/stac-utils/stactools/workflows/CI/badge.svg)
[![Documentation](https://readthedocs.org/projects/stactools/badge/?version=latest)](https://stactools.readthedocs.io/en/latest/)
[![PyPI version](https://img.shields.io/pypi/v/stactools)](https://pypi.org/project/stactools/)
[![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/stactools)](https://anaconda.org/conda-forge/stactools)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

`stactools` is a high-level command line tool and Python library for working with [STAC](https://stacspec.org).
It is based on [PySTAC](https://github.com/stac-utils/pystac).

This is the core `stactools` repository, which provides a basic command line interface (CLI) and API for working with STAC catalogs.
There are a suite of packages available in other repositories for working with a variety of datasets and for doing more complicated operations on STAC data.
See [packages](#packages) for more information.

## Table of Contents

- [Installation](#installation)
- [Running](#running)
- [Documentation](#documentation)
- [Packages](#packages)
- [Developing](#developing)

## Installation

To install the latest version via pip:

```sh
pip install stactools
```

To install the latest version with [conda](https://docs.conda.io/en/latest/):

```sh
conda install -c conda-forge stactools
```

To install the latest development version from the source repository:

```sh
git clone https://github.com/stac-utils/stactools.git
cd stactools
pip install .
```

**NOTE:** In order to read and write Cloud Optimized Geotiffs, GDAL version 3.1 or greater is required.
If your system GDAL is older than version 3.1, consider using [Docker](#using-docker) or [Conda](#using-conda) to get a modern GDAL.

### Optional dependencies

`stactools` includes one optional dependency:

- `s3`: Enables s3 hrefs via `fsspec` and `s3fs`

To install the single optional dependency:

```sh
pip install stactools[s3]
```

### Docker

To download the Docker image from the registry:

```sh
docker pull ghcr.io/stac-utils/stactools:latest
```

## Running

```sh
stac --help
```

### Docker

```sh
docker run --rm ghcr.io/stac-utils/stactools:latest --help
```

## Documentation

See the [documentation page](https://stactools.readthedocs.io/en/latest/) for the latest docs.

## Packages

`stactools` is comprised of many other sub-packages that provide library and CLI functionality.
Officially supported packages are hosted in the Github [`stactools-packages` organization](https://github.com/stactools-packages/stactools-packages.github.io), and other subpackages may be available from other sources.

There are over 25 packages that translate specific types of data into STAC,
including imagery sources like
[aster](https://github.com/stactools-packages/aster),
[landsat](https://github.com/stactools-packages/landsat),
[modis](https://github.com/stactools-packages/modis),
[naip](https://github.com/stactools-packages/naip),
[planet](https://github.com/stactools-packages/planet),
[sentinel1](https://github.com/stactools-packages/sentinel1),
[sentinel1-grd](https://github.com/stactools-packages/sentinel1-grd),
[sentinel2](https://github.com/stactools-packages/sentinel2),
[sentinel3](https://github.com/stactools-packages/sentinel3), landuse/landcover
data ([corine](https://github.com/stactools-packages/corine),
[cgls_lc100](https://github.com/stactools-packages/cgls_lc100),
[aafc-landuse](https://github.com/stactools-packages/aafc-landuse)), Digital
Elevation Models (DEMs)
([cop-dem](https://github.com/stactools-packages/cop-dem),
[alos-dem](https://github.com/stactools-packages/alos-dem)), population data
([gpw](https://github.com/stactools-packages/gpw),
[worldpop](https://github.com/stactools-packages/worldpop)),
[pointclouds](https://github.com/stactools-packages/pointcloud) and many more.

There are also cool tools like [stactools-browse](https://github.com/stactools-packages/stactools-browse) which makes it super easy to deploy a
[STAC Browser](https://github.com/radiantearth/stac-browser) from the command line to browse any local data.

For the list of officially supported packages see the [list of STAC packages](https://github.com/stactools-packages/stactools-packages.github.io#list-of-stac-packages)
on the [stactools-packages GitHub organization](https://github.com/stactools-packages).
Each package can be installed via `pip install stactools-{package}`, e.g. `pip install stactools-landsat`.
Third-party packages can be installed in the same way, or, if they are not on PyPI, directly from the source repository, e.g. `pip install /path/to/my/code/stactools-greatdata`.

## Developing

Basic development can be done with your system's default Python, though it it recommended to use a virtual environment.
E.g.:

```sh
git clone https://github.com/stac-utils/stactools.git
cd stactools
python -m venv venv
pip install -e .  # install stactools into the virtual environment in editable mode
pip install -r requirements-dev.txt  # install development requirements
```

Linting and formatting are handled with [pre-commit](https://pre-commit.com/).
You will need to install pre-commit before committing any changes:

```sh
pre-commit install
```

Tests are handled with [pytest](https://docs.pytest.org/en/7.1.x/):

```sh
pytest
```

Run a Juypter notebook:

```sh
scripts/notebook
```

### Using docker

You can also develop in a Docker container.
Build the container with:

```sh
docker/build
```

Once the container is built, you can run the `scripts/` scripts inside a docker console by running:

```sh
docker/console
```

A complete build and test can be run with:

```sh
docker/cibuild
```

In scenarios where you want to run scripts in `docker/` but don't want to run the build, images can be downloaded via the `pull` script:

```sh
docker/pull
```

Run a [Juypter](https://jupyter.org/) notebook:

```sh
docker/notebook
```

You can run the CLI through docker by running:

```sh
docker/stac --help
```

### Using conda

[conda](https://docs.conda.io/en/latest/) is a useful tool for managing dependencies, both binary and Python-based.
If you have conda installed, you can create a new environment for `stactools` development by running the following command from the top-level directory in this repo:

```sh
conda env create -f environment.yml
```

Then activate the `stactools` environment:

```sh
conda activate stactools
```

Finally, install `stactools` in editable mode and all development requirements:

```sh
pip install -e .
pip install -r requirements-dev.txt
```

### Documentation

To build and serve the docs, the development requirements must be installed with `pip install -r requirements-dev.txt`.
To build the docs, you can use `make html` from inside of the docs directory, and to build the docs and start a server that watches for changes, use `make livehtml`:

```sh
cd docs
make html
make livehtml
```

If using `make livehtml`, once the server starts, navigate to [http://localhost:8000](http://localhost:8000/) to see the docs.
Use 'make' without arguments to see a list of available commands.

You can also run the previous commands in the docker container using:

```sh
docker/console
```

### Code owners and repository maintainer(s)

This repository uses a [code owners file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) to automatically request reviews for new pull requests.
The current primary maintainer(s) of this repository are listed under the `*` rule in the [CODEOWNERS](./CODEOWNERS) file.

### Adding a new package

To create a new `stactools` package, use the [`stactools` package template](https://github.com/stactools-packages/template).
`stactools` utilizes Python's [namespace packages](https://packaging.python.org/guides/packaging-namespace-packages/) to provide a suite of tools all under the `stactools` namespace.
If you would like your package to be considered for inclusion as a core `stactools` package, please open an issue on this repository with a link to your package repository.

### Releasing

See [RELEASING.md](./RELEASING.md) for the steps to create a new release.
