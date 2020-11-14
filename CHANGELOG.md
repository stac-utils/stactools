# Changelog

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
