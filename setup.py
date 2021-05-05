from setuptools import setup, find_namespace_packages

install_requires = [
    line.strip() for line in open('requirements.txt').readlines()
    if not line.startswith("#")
]

setup(name='stactools',
      version="0.1.4",
      description=(
          "Command line tool and Python library for working with STAC."),
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      author="stac-utils",
      author_email='stac@radiant.earth',
      url='https://github.com/stac-utils/stactools.git',
      packages=find_namespace_packages(),
      include_package_data=False,
      install_requires=install_requires,
      license="Apache Software License 2.0",
      keywords=['stactools', 'psytac', 'imagery', 'raster', 'catalog', 'STAC'],
      test_suite='tests')
