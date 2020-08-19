import os
from imp import load_source
from setuptools import setup, find_packages
from glob import glob
import io

__version__ = load_source('stactools.version', 'stactools/version.py').__version__

from os.path import (
    basename,
    splitext
)

here = os.path.abspath(os.path.dirname(__file__))

# get the dependencies and installs
with io.open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    install_requires = f.read().split('\n')

with open(os.path.join(here, 'README.md')) as readme_file:
    readme = readme_file.read()

setup(
    name='stactools',
    version=__version__,
    description=("Command line tool and Python library for working with STAC."),
    long_description=readme,
    long_description_content_type="text/markdown",
    author="stac-utils",
    author_email='stac@radiant.earth',
    url='https://github.com/stac-utils/stactools.git',
    packages=find_packages(),
    py_modules=[splitext(basename(path))[0] for path in glob('stactools/*.py')],
    include_package_data=False,
    install_requires=install_requires,
    license="Apache Software License 2.0",
    keywords=[
        'stactools',
        'psytac',
        'imagery',
        'raster',
        'catalog',
        'STAC'
    ],
    entry_points={
        'console_scripts': ['stactools=stactools.cli:cli'],
    },
    test_suite='tests'
)
