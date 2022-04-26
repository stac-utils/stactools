# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- CI check for Python 3.10 (requires pre-release version of rasterio 1.3) ([#271](https://github.com/stac-utils/stactools/pull/271))
- pre-commit and isort ([#275](https://github.com/stac-utils/stactools/pull/275))
- More API documentation ([#282](https://github.com/stac-utils/stactools/pull/282))

### Changed

- Skip Click v8.1.0 as it broke decorator typing ([#266](https://github.com/stac-utils/stactools/pull/266))
- Use black (instead of yapf) for formatting ([#274](https://github.com/stac-utils/stactools/pull/274))
- stac-check version and lint reporting ([#258](https://github.com/stac-utils/stactools/pull/258))
- Sphinx theme ([#284](https://github.com/stac-utils/stactools/pull/284))

### Fixed

- Antimeridian winding order ([#278](https://github.com/stac-utils/stactools/pull/278))

## [0.3.0] - 2022-03-25

### Added

- Documentation on the release process ([#241](https://github.com/stac-utils/stactools/pull/241))
- `stac lint` using [stac-check](https://github.com/philvarner/stac-check) ([#254](https://github.com/stac-utils/stactools/pull/254))
- `stac info` now has option `-s` or `--skip_items` to skip counting and printing catalog item info ([#260](https://github.com/stac-utils/stactools/pull/260))
- updated `livehtml` target for documentation build to work with latest `sphinx-autobuild` ([#261](https://github.com/stac-utils/stactools/pull/261))
- Antimeridian helpers ([#259](https://github.com/stac-utils/stactools/pull/259))

## [0.2.6] - 2022-02-15

### Added

- CI checks for minimum and pre-release versions of dependencies ([#228](https://github.com/stac-utils/stactools/pull/228))

### Fixed

- Test items are now valid STAC v1.0.0 ([#243](https://github.com/stac-utils/stactools/pull/243))
- Move asset tests now have all the assets they need ([#243](https://github.com/stac-utils/stactools/pull/243))
### Changed

- Use [pytest](https://docs.pytest.org/) for unit testing instead of `unittest` ([#220](https://github.com/stac-utils/stactools/pull/220))
- Signature of `stactools.core.utils.convert.cogify` ([#222](https://github.com/stac-utils/stactools/pull/222))
- Don't push Docker images from pull requests ([#225](https://github.com/stac-utils/stactools/pull/225), [#226](https://github.com/stac-utils/stactools/pull/226))

### Removed

- GDAL Python bindings dependency ([#222](https://github.com/stac-utils/stactools/pull/222))
- Upper bounds on dependencies ([#228](https://github.com/stac-utils/stactools/pull/228))

## [0.2.5] - 2022-01-03

### Added

- `read_href_modifer` argument to `stactools.create.item` ([#212](https://github.com/stac-utils/stactools/pull/212))

## [0.2.4] - 2021-11-23

### Added

- `addraster` command ([#204](https://github.com/stac-utils/stactools/pull/204)), including `gdal` Python dependency

### Changed

- Update to pystac 1.2 ([#209](https://github.com/stac-utils/stactools/pull/209))
- Update click to 8.0.x ([#209](https://github.com/stac-utils/stactools/pull/209))
  - Any packages using `types-click` should remove that package. Version 8 adds proper type annotations to the main package.
- Set mypy to `strict` ([#209](https://github.com/stac-utils/stactools/pull/209))

### Fixed

- Readthedocs build ([#210](https://github.com/stac-utils/stactools/pull/210))

## [0.2.3] - 2021-09-16

### Added

- `stactools.core.create.item` and associated CLI subcommand ([#201](https://github.com/stac-utils/stactools/pull/201))
- `stactools.core.add.add_item` and associated CLI command for adding an item to a Catlog/Collection ([#153](https://github.com/stac-utils/stactools/pull/153))

### Fixed

- Typing for Python 3.7 in `stactools.core.projection` ([#201](https://github.com/stac-utils/stactools/pull/201))

## [0.2.2] - 2021-09-13

### Added

- Add the ability to use data from the Microsoft Planetary Computer as external testing data ([#197](https://github.com/stac-utils/stactools/pull/197))

### Changed

- Improved error reporting and documentation for old GDAL versions.
  GDAL 3.1 is required to read and write Cloud Optimized Geotiffs.
  ([#194](https://github.com/stac-utils/stactools/pull/194))

### Fixed

- ReadTheDocs ([#190](https://github.com/stac-utils/stactools/pull/190))
- Typing in the projection module ([#198](https://github.com/stac-utils/stactools/pull/198))

## [0.2.1] - 2021-07-28

The v0.2 release of stactools is a major refactor of the packaging and organization strategy for stactools.
Most packages have been moved to the [stactools-packages](https://github.com/stactools-packages) organizing, leaving only `stactools.core`, `stactools.cli`, and the new `stactools.testing` packages in this repository.

### Added

- Adds `stactools.testing`, which provides an API with convenience functions for packages to use in their testing code.
  Replaces `tests/utils`.
- Add `mypy` as a lint dependency.
  Also publish type information for when `stactools` is used as a library. ([#182](https://github.com/stac-utils/stactools/pull/182))
- Optional dependency on s3fs ([#178](https://github.com/stac-utils/stactools/pull/178)), enabling:
  - Using s3 files as external data for testing
  - Using s3 hrefs with stactools functionality by installing with `pip install stactools[s3]` (or `pip install stactools[all]`)
- `stac validate` command for validating JSON and checking links ([#151](https://github.com/stac-utils/stactools/pull/151))
- `docker/pull` script for downloading Docker images
- GitHub issue and PR templates
- `script/notebook` to run Jupyter notebooks ([#174](https://github.com/stac-utils/stactools/pull/174))

### Changed

- Separates dataset packages and `stactools.browse` into a new Github organization, [stactools-packages](https://github.com/stactools-packages)
- Updated PySTAC dependency to `~= 1.1` ([#185](https://github.com/stac-utils/stactools/pull/185))
- Restructured the Docker build
- Using GitHub Docker Registry rather than DockerHub for storing images
- Use both PySTAC and STAC version in version command ([#149](https://github.com/stac-utils/stactools/pull/149))
- Bumped `rasterio` version to v1.2

### Removed

- Dropped support for Python 3.6
- `validate_cloud_optimized_geotiff.py`

## [0.1.6] - 2021-06-09

### Added

- Band assets for lower spatial resolution version of Sentinel 2 L2A ([#88](https://github.com/stac-utils/stactools/pull/88))
- Version command ([#127](https://github.com/stac-utils/stactools/pull/127))

### Changed

- Better handling for Skysat images and other Planet improvements ([#73](https://github.com/stac-utils/stactools/pull/73))
- Use core utilities in more subpackages ([#112](https://github.com/stac-utils/stactools/pull/112))

### Fixed

- Converted landsat tests to local instead of network access ([#105](https://github.com/stac-utils/stactools/pull/105))
- Update landsat convert script to take new USGS fields ([#109](https://github.com/stac-utils/stactools/pull/109))
- Typo in Sentinel 2 L2A items ([#116](https://github.com/stac-utils/stactools/pull/116))
- `--enable-proj` flag for landsat's convert command ([#94](https://github.com/stac-utils/stactools/pull/94))
- Small documentation typo ([#119](https://github.com/stac-utils/stactools/pull/119))
- Removed leftover debugging code in sentinel2 test ([#118](https://github.com/stac-utils/stactools/pull/118))
- Landsat8 bounding boxes were off by half of a pixel ([#121](https://github.com/stac-utils/stactools/pull/121))
- Zero-valued z coordinates in sentinel2 metadata ([#122](https://github.com/stac-utils/stactools/pull/122))
- SA_QA_AEROSOL asset key in landsat data ([#126](https://github.com/stac-utils/stactools/pull/126))
- Relative paths in sentinel2 assets ([#125](https://github.com/stac-utils/stactools/pull/125))

## [0.1.5] - 2021-05-06

### Added

- Method for creating Copernicus Land Cover Layers ([#50](https://github.com/stac-utils/stactools/pull/50))
- `eo:bands` information for Planet SkySat assets ([#40](https://github.com/stac-utils/stactools/issues/40))
- Roles and thumbnails for Planet assets ([#46](https://github.com/stac-utils/stactools/issues/46) and [#49](https://github.com/stac-utils/stactools/issues/49))
- Projection information for Planet items ([#39](https://github.com/stac-utils/stactools/issues/39))
- Azimuth values in the view namespace for Planet ([#59](https://github.com/stac-utils/stactools/issues/59))
- More Planet properties ([#57](https://github.com/stac-utils/stactools/issues/57))
- Add "via" rel link for Planet data ([#58](https://github.com/stac-utils/stactools/issues/58))
- Sentinel-2 item creation ([#52](https://github.com/stac-utils/stactools/pull/52))
- Top level symlink directory to help the dev environment.
- Merge command ([#75](https://github.com/stac-utils/stactools/pull/75))
- USGS 3DEP support as `threedep` ([#81](https://github.com/stac-utils/stactools/pull/81))

### Changed

- Allow debug output in unit tests
- Updates to `aster`, `landsat`, and `sentinel2` subpackages ([#83](https://github.com/stac-utils/stactools/pull/83))

### Fixed

- Landsat projection extraction ([#67](https://github.com/stac-utils/stactools/pull/67) and [#100](https://github.com/stac-utils/stactools/pull/100))
- Installing `naip` subpackage ([#72](https://github.com/stac-utils/stactools/pull/72))
- Clean up planet test data ([#74](https://github.com/stac-utils/stactools/pull/74))
- `aster` COG generation ([#89](https://github.com/stac-utils/stactools/pull/89))
- `landsat` asset keys ([#90](https://github.com/stac-utils/stactools/pull/90))
- Docs ([#93](https://github.com/stac-utils/stactools/pull/93))

## [0.1.4] - 2021-02-21

### Added
- Implementation of Landsat STAC handling ([#23](https://github.com/stac-utils/stactools/pull/23))
- Add NAIP subpackage for deriving NAIP STAC items and collection ([#18](https://github.com/stac-utils/stactools/pull/18))
- Add catalog type option for `planet convert` ([#61](https://github.com/stac-utils/stactools/pull/61))

## [0.1.3] - 2021-01-19

### Added

- Add method for creating CORINE Land Cover. ([#33](https://github.com/stac-utils/stactools/pull/33))

### Fixed

- Fix issue caused by mihandling of shapely bounds returning tuple. ([#41](https://github.com/stac-utils/stactools/pull/41))

## [0.1.2] - 2021-01-14

### Added

- Added ASTER package ([#16](https://github.com/stac-utils/stactools/pull/16))

### Fixed

- Fixed issues with copying and asset movint ([#34](https://github.com/stac-utils/stactools/pull/34))
- Fix `stac browse` with upgrades to versions in the tiler container ([#35](https://github.com/stac-utils/stactools/pull/35))

## [0.1.1] - 2020-11-14

See [#9](https://github.com/stac-utils/stactools/pull/9)

### Added

- Add docs to note that stac copy will migrate the copied STAC to the latest version.

### Changed

- Add -h as shortcut for --include-hrefs option in stac describe.

### Fixed

- Include all Planet item metadata, using 'pl:' for a prefix to any metadata that doesn't map to STAC
- Fixed bug in stac merge when copying assets
- Update collection extents when using stac merge

## [0.1.0] - 2020-10-30

### Added

- `stac planet` commands for converting Planet orders to STACs.
- `stac.cli.command.copy` commands for copying and moving STACs and assets.
- `stac.cli.command.layout` for modfiygin the layout of STACs
- `stac.browse` for launching a local instance of stac-browser using docker.

[Unreleased]: <https://github.com/stac-utils/stactools/compare/v0.3.0..main>
[0.3.0]: <https://github.com/stac-utils/stactools/compare/v0.2.6..v0.3.0>
[0.2.6]: <https://github.com/stac-utils/stactools/compare/v0.2.5..v0.2.6>
[0.2.5]: <https://github.com/stac-utils/stactools/compare/v0.2.4..v0.2.5>
[0.2.4]: <https://github.com/stac-utils/stactools/compare/v0.2.3..v0.2.4>
[0.2.3]: <https://github.com/stac-utils/stactools/compare/v0.2.2..v0.2.3>
[0.2.2]: <https://github.com/stac-utils/stactools/compare/v0.2.1..v0.2.2>
[0.2.1]: <https://github.com/stac-utils/stactools/compare/v0.1.6..v0.2.1>
[0.1.6]: <https://github.com/stac-utils/stactools/compare/v0.1.5..v0.1.6>
[0.1.5]: <https://github.com/stac-utils/stactools/compare/v0.1.4..v0.1.5>
[0.1.4]: <https://github.com/stac-utils/stactools/compare/v0.1.3..v0.1.4>
[0.1.3]: <https://github.com/stac-utils/stactools/compare/v0.1.2..v0.1.3>
[0.1.2]: <https://github.com/stac-utils/stactools/compare/v0.1.1..v0.1.2>
[0.1.1]: <https://github.com/stac-utils/stactools/compare/v0.1.0..v0.1.1>
[0.1.0]: <https://github.com/stac-utils/stactools/releases/tag/v0.1.0>
