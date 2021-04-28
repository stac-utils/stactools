import os
from os.path import (basename, splitext)
from imp import load_source
from setuptools import setup, find_namespace_packages
from glob import glob
import io

name = 'stactools_threedep'
description = ("Subpackage for working with 3DEP data in stactools, "
               "a command line tool and Python library for working with STAC.")

__version__ = load_source(
    'stactools.threedep.version',
    os.path.join(os.path.dirname(__file__),
                 'stactools/threedep/version.py')).__version__

here = os.path.abspath(os.path.dirname(__file__))

# get the dependencies and installs
with io.open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    install_requires = [line.split(' ')[0] for line in f.read().split('\n')]

# Add stactools subpackage dependencies
install_requires.extend(['stactools_core=={}'.format(__version__)])

with open(os.path.join(here, 'README.md')) as readme_file:
    readme = readme_file.read()

setup(name=name,
      description=description,
      version=__version__,
      long_description=readme,
      long_description_content_type="text/markdown",
      author="Pete Gadomski",
      author_email='pgadomski@element84.com',
      url='https://github.com/stac-utils/stactools.git',
      packages=find_namespace_packages(),
      py_modules=[
          splitext(basename(path))[0] for path in glob('stactools/*.py')
      ],
      include_package_data=False,
      install_requires=install_requires,
      license="Apache Software License 2.0",
      keywords=[
          'stactools', 'psytac', '3DEP', 'NED', 'DEM', 'elevation', 'raster',
          'catalog', 'STAC'
      ])
