import os
from imp import load_source
from setuptools import setup, find_packages
from glob import glob
import io

__version__ = load_source('stactools.core.version',
                          os.path.join(
                              os.path.dirname(__file__),
                              'stactools_core/stactools/core/version.py'
                          )).__version__

from os.path import (
    basename,
    splitext
)

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as readme_file:
    readme = readme_file.read()

# These subpackages will be installed by default
default_subpackages=[
    'stactools_core=={}'.format(__version__),
    'stactools_cli=={}'.format(__version__)
]

# List subpackages as extras
extras_require={
    'all': [
        'stactools_landsat=={}'.format(__version__),
        'stactools_planet=={}'.format(__version__),
        'stactools_browse=={}'.format(__version__)
    ],
    'landsat': ['stactools_landsat=={}'.format(__version__)],
    'planet': ['stactools_planet=={}'.format(__version__)],
    'browse': ['stactools_browse=={}'.format(__version__)]
}

setup(
    name='stactools',
    version=__version__,
    description=("Command line tool and Python library for working with STAC."),
    long_description=readme,
    long_description_content_type="text/markdown",
    author="stac-utils",
    author_email='stac@radiant.earth',
    url='https://github.com/stac-utils/stactools.git',
    packages=[],
    py_modules=[splitext(basename(path))[0] for path in glob('stactools/*.py')],
    include_package_data=False,
    install_requires=default_subpackages,
    extras_require=extras_require,
    license="Apache Software License 2.0",
    keywords=[
        'stactools',
        'psytac',
        'imagery',
        'raster',
        'catalog',
        'STAC'
    ],
    test_suite='tests'
)
