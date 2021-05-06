# Changelog

## [unreleased]

## stactools 0.1.5

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

## stactools 0.1.4

### Added
- Implementation of Landsat STAC handling ([#23](https://github.com/stac-utils/stactools/pull/23))
- Add NAIP subpackage for deriving NAIP STAC items and collection ([#18](https://github.com/stac-utils/stactools/pull/18))
- Add catalog type option for `planet convert` ([#61](https://github.com/stac-utils/stactools/pull/61))

## stactools 0.1.3

### Added

- Add method for creating CORINE Land Cover. ([#33](https://github.com/stac-utils/stactools/pull/33))

### Fixed

- Fix issue caused by mihandling of shapely bounds returning tuple. ([#41](https://github.com/stac-utils/stactools/pull/41))

## stactools 0.1.2

### Added

- Added ASTER package ([#16](https://github.com/stac-utils/stactools/pull/16))

### Fixed

- Fixed issues with copying and asset movint ([#34](https://github.com/stac-utils/stactools/pull/34))
- Fix `stac browse` with upgrades to versions in the tiler container ([#35](https://github.com/stac-utils/stactools/pull/35))

## stactools 0.1.1

See [#9](https://github.com/stac-utils/stactools/pull/9)

### Added

- Add docs to note that stac copy will migrate the copied STAC to the latest version.

### Changed

- Add -h as shortcut for --include-hrefs option in stac describe.

### Fixed

- Include all Planet item metadata, using 'pl:' for a prefix to any metadata that doesn't map to STAC
- Fixed bug in stac merge when copying assets
- Update collection extents when using stac merge

## stactools 0.1

### Added

- `stac planet` commands for converting Planet orders to STACs.
- `stac.cli.command.copy` commands for copying and moving STACs and assets.
- `stac.cli.command.layout` for modfiygin the layout of STACs
- `stac.browse` for launching a local instance of stac-browser using docker.
