## stactools
![Build Status](https://github.com/stac-utils/stactools/workflows/CI/badge.svg?branch=develop)
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
> pip install stactools_landsat
```

```bash
> pip install stactools[landsat]
```


| install command                    | description                                                         |
| ---------------------------------- | ------------------------------------------------------------------- |
| pip install stactools[all]         | Installs all available subpackages contained in the stac-tools repo |
| pip install stactools[landsat]     | Installs the [landsat] subpackage for working with landsat data     |


## Running

```
> stactools --help
```

## Documentation

See the [documentation page](https://stactools.readthedocs.io/en/latest/) for the latest docs.

## Developing

### Using virtualenv

It's recommended to use [virtualenv](https://virtualenv.pypa.io/en/latest/index.html) to keep isolate the python environment used to develop stactools. See virtualenv documentation for more detailed information, but as a shortcut here's some quick steps:

- Make sure [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) is installed
- Run `virtualenv venv`
- Activate the virtualenv with `source venv/bin/active`

### Installing development requirements

To install all the requirements for subpackages and the development requirements, use:

```
> scripts/update
```

### Running the CLI against development code

You can run the CLI through the source code by running

```
> scripts/stac --help
```

## Sub-packages

`stactools` is comprised of subpackages that provide library and CLI functionality. Below is a list of available subpackages.

| subpackage                    | description                                                                   |
| ----------------------------- | ----------------------------------------------------------------------------- |
| `stactools_core`              | Contains core library functionality that is used across the other projects    |
| `stactools_cli`               | Contains the command line interface (cli) for runnign the `stactools` command |
| `stactools_landsat`           | Contains methods and commands for working with landsat data                   |

Subpackages are symlinked to the `stactools` directory in this repo to allow them to be importable for python running at the top level directory of the repository clone.

### Unit Tests

Unit tests are in the `tests` folder. To run unit tests, use `unittest`:

```
> python -m unittest discover tests
```

To run linters, code formatters, and test suites all together, use `test`:

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

You can also run the `./scripts/test` script to check flake8 and yapf.

### Documentation

To build and develop the documentation locally, make sure sphinx is available (which is installed with `requirements-dev.txt`), and use the Makefile in the docs folder:

```
> cd docs
> make html
> make livehtml
```

Use 'make' without arguments to see a list of available commands.
