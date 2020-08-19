## stactools
![Build Status](https://github.com/stac-utils/pystac/workflows/CI/badge.svg?branch=develop)
[![PyPI version](https://badge.fury.io/py/pystac.svg)](https://badge.fury.io/py/pystac)
[![Documentation](https://readthedocs.org/projects/pystac/badge/?version=latest)](https://pystac.readthedocs.io/en/latest/)
[![codecov](https://codecov.io/gh/stac-utils/pystac/branch/develop/graph/badge.svg)](https://codecov.io/gh/stac-utils/pystac)
[![Gitter chat](https://badges.gitter.im/azavea/pystac.svg)](https://gitter.im/azavea/pystac)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

`stactools` is a command line tool and library for working with [STAC](https://stacspec.org) based on [PySTAC](https://github.com/stac-utils/pystac).

## Installation

```bash
> pip install stactools
```
From source repository:

```bash
> git clone https://github.com/stac-utils/stactools.git
> cd stactools
> pip install .
```

## Running

```
> stactools --help
```

#### Versions
To install a specific versions of STAC, install the matching version of stactools.

```bash
> pip install stactools==0.1.*
```

The table below shows the corresponding versions between pystac and STAC:

| stactools | STAC  |
| --------- | ----- |
| 0.1.x     | 1.0.x |

## Documentation

See the [documentation page](https://stactools.readthedocs.io/en/latest/) for the latest docs.

## Developing

To ensure development libraries are installed, install everything in `requirements-dev.txt`:

```
> pip install -r requirements-dev.txt
```

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
> flake8 stactools
> flake8 tests
```

To format code:

```
> yapf -ipr stactools
> yapf -ipr tests
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
