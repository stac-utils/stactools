import os
from os.path import (
    basename,
    splitext
)
from imp import load_source
from setuptools import setup, find_packages
from glob import glob
import io

class Subpackage:
    def __init__(self, name, is_extra=False):
        self.name = name
        self.is_extra = is_extra

    @property
    def version(self):
        version_file = 'stactools_{}/stactools/{}/version.py'.format(self.name, self.name)
        return load_source('stactools.{}.version'.format(self.name),
                          os.path.join(
                              os.path.dirname(__file__),
                              version_file
                          )).__version__

    @property
    def requirement_name(self):
        return 'stactools_{}=={}'.format(self.name, self.version)

subpackages = [
    Subpackage('core'),
    Subpackage('cli'),
    Subpackage('aster', is_extra=True),
    Subpackage('landsat', is_extra=True),
    Subpackage('planet', is_extra=True),
    Subpackage('browse', is_extra=True),
]

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as readme_file:
    readme = readme_file.read()

# These subpackages will be installed by default
default_subpackages=[
    p.requirement_name for p in subpackages if not p.is_extra
]

# List subpackages as extras
extras_require={
    'all': []
}

for p in subpackages:
    if p.is_extra:
        extras_require[p.name] = [p.requirement_name]
        extras_require['all'].append(p.requirement_name)

version = max([p.version for p in subpackages])

setup(
    name='stactools',
    version=version,
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
