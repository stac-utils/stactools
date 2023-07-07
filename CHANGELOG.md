# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- For raster footprints users can set destination CRS rather than it being hardcoded to EPSG:4326 ([#440](https://github.com/stac-utils/stactools/pull/440))
- Raster footprint calculation for multi-asset items can elect to use the union or intersection of the asset footprints ([#445](https://github.com/stac-utils/stactools/pull/445))
- On `stac create-item` asset key name and roles are settable ([#442](https://github.com/stac-utils/stactools/pull/442))

### Changed

- Update pystac dependency to 0.7 and shapely to 2.0 ([#441](https://github.com/stac-utils/stactools/pull/441))

### Fixed

- `copy --copy-assets` now works even with relative asset hrefs ([#436](https://github.com/stac-utils/stactools/pull/436))

### Deprecated

- Many functions in `stactools.testing.CliTestCase` ([#447](https://github.com/stac-utils/stactools/pull/447)).
- `raster_footprint.reproject_polygon` and `projection.reproject_geom`. Use `projection.reproject_shape` instead with `shapely.Geometry` objects as the input and output ([#441](https://github.com/stac-utils/stactools/pull/441))

### Removed

- Unused files under `tests/data-files` ([#438](https://github.com/stac-utils/stactools/pull/438))


## [0.4.8] - 2023-06-01

### Added

- `--no-resolve-links` to the copy command ([#430](https://github.com/stac-utils/stactools/pull/430))

### Changed

- Use `pyproject.toml` for project metadata ([#424](https://github.com/stac-utils/stactools/pull/424))
- Use <https://pypi.org/project/antimeridian> for antimeridian and pole fixes ([#426](https://github.com/stac-utils/stactools/pull/426)).
  Note that this _may_ change the output geometries when fixing some antimeridian-crossing polygons, e.g. if the input polygons are wound clockwise (instead of counter-clockwise), the output geometry will be unexpectedly large (<https://github.com/gadomski/antimeridian/issues/33>).

### Fixed

- Bounding boxes after fixing geometries for antimeridian crossings ([#432](https://github.com/stac-utils/stactools/pull/432))

### Deprecated

- Many functions in `stactools.core.utils.antimeridian` ([#426](https://github.com/stac-utils/stactools/pull/426)).
  Users should use the [antimeridian](https://pypi.org/project/antimeridian) package instead, or in the case "normalization", don't normalize at all since it doesn't conform to the GeoJSON spec.
  These are the deprecated functions:
  - `split`
  - `split_multipolygon`
  - `normalize`
  - `normalize_multipolygon`
  - `enclose_poles`

## [0.4.7] - 2023-05-08

### Changed

- Transformation failures in `reproject_geom` now throw an error ([#420](https://github.com/stac-utils/stactools/pull/420))

## [0.4.6] - 2023-04-10

### Added

- `enclose_poles` to the antimeridian module ([#416](https://github.com/stac-utils/stactools/pull/416))

### Fixed

- `densify_by_distance` now includes the points in the original coordinate list in the returned densified coordinate list ([#412](https://github.com/stac-utils/stactools/pull/412))
- `densify_by_factor` now includes the final coordinate in the original coordinate list in the returned densifed coordinate list ([#412](https://github.com/stac-utils/stactools/pull/412))
- The `footprint` method on the `RasterFootprint` class now always returns counter-clockwise polygons in line with the GeoJSON specification ([#412](https://github.com/stac-utils/stactools/pull/412))

### Changed

- `update_geometry_from_asset_footprint` in the raster_footprint module now updates the Item bbox based on the updated geometry extents ([#414](https://github.com/stac-utils/stactools/pull/414))

## [0.4.5] - 2023-03-24

### Added

- Add `update-extent` subcommand to the CLI ([#405](https://github.com/stac-utils/stactools/pull/405))

### Changed

- Format of subdataset names when creating cogs ([#407](https://github.com/stac-utils/stactools/pull/407))
- Use [ruff](https://github.com/charliermarsh/ruff) instead of flake8 and isort ([#407](https://github.com/stac-utils/stactools/pull/407))

## [0.4.4] - 2023-02-16

### Added

- `stactools.core.utils.round` for rounding Item geometry and Item and Collection bboxes to a specified precision ([#384](https://github.com/stac-utils/stactools/pull/384))
- `stactools.core.utils.raster_footprint.densify_by_distance` for densifying polygons at distance intervals ([#396](https://github.com/stac-utils/stactools/pull/396))
- `stactools.core.utils.raster_footprint.reproject_polgyon` for reprojecting a polygon and removing duplicate vertices caused by rounding ([#396](https://github.com/stac-utils/stactools/pull/396))
- `stactools.core.utils.raster_footprint.RasterFootprint` class for customizing raster data footrpint creation behaviour via subclassing ([#396](https://github.com/stac-utils/stactools/pull/396))

### Changed

- Freed `recursive_round` function from `round_coordinates` in `stactools.core.utils.round` ([#390](https://github.com/stac-utils/stactools/pull/390))
- Exposed the private `_densify` function as `densify_by_factor` in `stactools.core.utils.raster_footprint` ([#396](https://github.com/stac-utils/stactools/pull/396))

### Deprecated

- `update_geometry_from_asset_footprint`, `data_footprints_for_data_assets`, and `data_footprint` functions will be removed from `stactools.core.utils.raster_footprint` in v0.6.0 ([#396](https://github.com/stac-utils/stactools/pull/396))

## [0.4.3] - 2022-12-16

### Added

- Include kwargs in io `read_text` for use with internal `fsspec.open` call. ([#372](https://github.com/stac-utils/stactools/pull/372))
- Python 3.11 support ([#376](https://github.com/stac-utils/stactools/pull/376))
- `stac summary` command ([#323](https://github.com/stac-utils/stactools/pull/323))

## [0.4.2] - 2022-09-15

### Added

- Multi-band support for raster footprint generation ([#355](https://github.com/stac-utils/stactools/pull/355))

### Fixed

- `stac create-item` JSON output ([#355](https://github.com/stac-utils/stactools/pull/355))

## [0.4.1] - 2022-08-08

### Fixed

- `stactools.core.utils.raster_footprint` now handles nan nodata values correctly ([#344](https://github.com/stac-utils/stactools/pull/344))

## [0.4.0] - 2022-08-01

### Added

- `stactools.core.geometry` for handling common geometrical operations like creating bounding boxes from GeoJSON ([#314](https://github.com/stac-utils/stactools/pull/314))
- Specify installation channel to use for all conda packages to avoid incompatibility ([#301](https://github.com/stac-utils/stactools/pull/301))
- Allow MultiPolygons when fixing antimeridian issues ([#317](https://github.com/stac-utils/stactools/pull/317))
- Conda package, via [conda-forge](https://anaconda.org/conda-forge/stactools) ([#324](https://github.com/stac-utils/stactools/pull/324))
- Context manager to ignore rasterio's NotGeoreferencedWarning ([#331](https://github.com/stac-utils/stactools/pull/331))
- `stactools.core.utils.raster_footprint` and `stac update-geometry`  to assist in populating the geometry of an Item from data coverage of its data assets ([#307](https://github.com/stac-utils/stactools/pull/307))
- `stactools.core.add_asset` and `stac add-asset` to add an asset to an item ([#300](https://github.com/stac-utils/stactools/pull/300))

### Changed

- Modified `stactools.core.utils.convert` with functions to export subdatasets from HDF files as separate COGs and
  single bands from multiband files ([#318](https://github.com/stac-utils/stactools/pull/318))
- Modified `stactools.core.utils.antimeridian.fix_item` to return the item and updated 2 unit tests ([#317](https://github.com/stac-utils/stactools/pull/317))
- Relaxed typing for cmd parameter for the CliTestCase.run_command in cli_test.py ([#312](https://github.com/stac-utils/stactools/pull/312))
- Cleaned up API documentation ([#315](https://github.com/stac-utils/stactools/pull/315))
- Renamed command `addraster` to `add-raster` ([#321](https://github.com/stac-utils/stactools/pull/321))

### Removed

- Unnecessary and incorrect `args` and `kwargs` from `StacIO` subclass ([#315](https://github.com/stac-utils/stactools/pull/315))
- Dropped support for Python 3.7 ([#313](https://github.com/stac-utils/stactools/pull/313))

## [0.3.1] - 2022-05-05

### Added

- CI check for Python 3.10 (requires pre-release version of rasterio 1.3) ([#271](https://github.com/stac-utils/stactools/pull/271))
- pre-commit and isort ([#275](https://github.com/stac-utils/stactools/pull/275))
- `stac info` now has option `-p` or `--progress` to update console output while reading the catalog ([#262](https://github.com/stac-utils/stactools/pull/262))
- More API documentation ([#282](https://github.com/stac-utils/stactools/pull/282))
- `FsspecStacIO.write_text_to_href` ([#291](https://github.com/stac-utils/stactools/pull/291))

### Changed

- Skip Click v8.1.0 as it broke decorator typing ([#266](https://github.com/stac-utils/stactools/pull/266))
- Use black (instead of yapf) for formatting ([#274](https://github.com/stac-utils/stactools/pull/274))
- stac-check version and lint reporting ([#258](https://github.com/stac-utils/stactools/pull/258))
- Sphinx theme ([#284](https://github.com/stac-utils/stactools/pull/284))
- Use stac-validator for validation ([#289](https://github.com/stac-utils/stactools/pull/289))

### Fixed

- Antimeridian winding order ([#278](https://github.com/stac-utils/stactools/pull/278))
- Test, lint, and format scripts ([#290](https://github.com/stac-utils/stactools/pull/290))

### Deprecated

- `FsspecStacIO.write_text_from_href` will be removed in v0.5.0 ([#291](https://github.com/stac-utils/stactools/pull/291))

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
- `stac.cli.command.layout` for modifying the layout of STACs
- `stac.browse` for launching a local instance of stac-browser using docker.

[Unreleased]: <https://github.com/stac-utils/stactools/compare/v0.4.8..main>
[0.4.8]: <https://github.com/stac-utils/stactools/compare/v0.4.7..v0.4.8>
[0.4.7]: <https://github.com/stac-utils/stactools/compare/v0.4.6..v0.4.7>
[0.4.6]: <https://github.com/stac-utils/stactools/compare/v0.4.5..v0.4.6>
[0.4.5]: <https://github.com/stac-utils/stactools/compare/v0.4.4..v0.4.5>
[0.4.4]: <https://github.com/stac-utils/stactools/compare/v0.4.3..v0.4.4>
[0.4.3]: <https://github.com/stac-utils/stactools/compare/v0.4.2..v0.4.3>
[0.4.2]: <https://github.com/stac-utils/stactools/compare/v0.4.1..v0.4.2>
[0.4.1]: <https://github.com/stac-utils/stactools/compare/v0.4.0..v0.4.1>
[0.4.0]: <https://github.com/stac-utils/stactools/compare/v0.3.1..v0.4.0>
[0.3.1]: <https://github.com/stac-utils/stactools/compare/v0.3.0..v0.3.1>
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
