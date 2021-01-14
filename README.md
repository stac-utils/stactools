## stactools
![Build Status](https://github.com/stac-utils/stactools/workflows/CI/badge.svg)
[![Documentation](https://readthedocs.org/projects/stactools/badge/?version=latest)](https://stactools.readthedocs.io/en/latest/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

`stactools` is a command line tool and library for working with [STAC](https://stacspec.org) based on [PySTAC](https://github.com/stac-utils/pystac).

## Installation

### Installing the base package


```bash
> pip install stactools
```

From source repository:

```bash
> git clone https://github.com/stac-utils/stactools.git
> cd stactools
> pip install .
```

To install stactools with all subpackages, use:

```bash
> git clone https://github.com/stac-utils/stactools.git
> cd stactools
> pip install .[all]
```

### Installing additional subpackages and plugins

`stactools` is composed of a namespace package with individual sub-packages installable on their own. This allows users to install only the parts of stactools that they need, and for new plugins with heavy dependencies to be developed without effecting the overall

```bash
> pip install stactools[all]
```

to install

```bash
> pip install stactools_planet
```

```bash
> pip install stactools[planet]
```


| install command                    | description                                                         |
| ---------------------------------- | ------------------------------------------------------------------- |
| pip install stactools[all]         | Installs all available subpackages contained in the stac-tools repo |
| pip install stactools[planet]      | Installs the `planet` subpackage for working with planet data       |


## Running

```
> stac --help
```

## Documentation

See the [documentation page](https://stactools.readthedocs.io/en/latest/) for the latest docs.

## Sub-packages

`stactools` is comprised of subpackages that provide library and CLI functionality. Below is a list of available subpackages.

| subpackage                    | description                                                                     |
| ------------------------------| ------------------------------------------------------------------------------- |
| `stactools_core`              | Contains core library functionality that is used across the other projects      |
| `stactools_cli`               | Contains the command line interface (cli) for running the `stactools` command   |
| `stactools_aster`             | Methods and commands for working with ASTER data                 |
| `stactools_corine`            | Methods and commands for working with CORINE Land Cover data                 |
| `stactools_planet`            | Methods and commands for working with planet data                |
| `stactools_landsat`           | Methods and commands for working with landsat data (TODO)        |
| `stactools_browse`            | Contains a command for launching stac-browser against a local STAC |

Subpackages are symlinked to the `stactools` directory in this repo to allow them to be importable for python running at the top level directory of the repository clone.

## Developing

### Using docker

Some subpackages require environments with more complex environments than can be set up just through pip. For example, the `stactools.aster` package uses rasterio functionality that required a GDAL enabled with the HDF4 format. Because of this, it's recommended to utilize the docker environment provided by this repository.

Once the container is built, you can run the `scripts/` scripts inside a docker console by running:

```
> docker/console
```

### Using virtualenv

If not using docker, itt's recommended to use [virtualenv](https://virtualenv.pypa.io/en/latest/index.html) to keep isolate the python environment used to develop stactools. See virtualenv documentation for more detailed information, but as a shortcut here's some quick steps:

- Make sure [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) is installed
- Run `virtualenv venv`
- Activate the virtualenv with `source venv/bin/active`

#### Installing development requirements

To install all the requirements for subpackages and the development requirements, use:

```
> scripts/update
```

Note that some packages might fail requirement installs because of required environment setup that cannot be controlled with pip-install. For instance, you may need to install rasterio with a GDAL that has non-standard formats enabled. You can avoid errors by installing the proper environment, by installing the failing requirements like rasterio manually, or by using the docker environment.

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

### Code quality checks

stactools uses [flake8](http://flake8.pycqa.org/en/latest/) and [yapf](https://github.com/google/yapf) for code formatting and style checks.

To run the flake8 style checks:

```
> flake8 stactools_* tests
```

To format code:

```
> yapf -ipr stactools_* tests
```

To check for spelling mistakes in modified files:

```
> git diff --name-only | xargs codespell -I .codespellignore -f
```

You can also run the `./docker/test` or `./scripts/test` script to check for linting, spelling, and run unit tests.

### Documentation

To build and serve the docs, all of the requirements must be installed with `scripts/update`. Make sure [Pandocs](https://pandoc.org/installing.html) is installed. Also make sure sphinx is available, which should be installed with `requirements-dev.txt`. You can also run the following in the docker container using

```
> docker/console
```

To build the docs, you can use `make html`, and to build the docs and start a server that watches for changes, use `make livhtml`:

```
> cd docs
> make html
> make livehtml
```

If using `make livehtml`, once the server starts, navigate to [http://localhost:8000](http://localhost:8000/) to see the docs.

Use 'make' without arguments to see a list of available commands.

### Adding a new sub-package

stactools is happy to take contributions of new subpackages for working with specific data types! Below is a list of steps to add a new subpackage:

- Add the new subpackage as `stactools_{pkg}`, where `{pkg}` is a short name for the dataset the subpackage works with (e.g. "landsat")
- Create a `setup.py`, `requirements.txt`, and `README.md` in the subpackage directory.
- The code should exist in the `stactools/{pkg}/` directory in that package subdirectory. Note that the `stactools` does not have an __init__.py (look at the other subpackages for examples).
- Add the subpackage to the appropriate variables in `scripts/env`
- Add the subpackage to the appropriate tables in the README.
- Add documentation for the subpackage.
- Add subpackage to .readthedocs.yml install
