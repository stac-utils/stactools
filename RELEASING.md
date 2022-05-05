# Releasing

To release a new version of **stactools** or a [stactools-package](https://github.com/stactools-packages/):

1. Determine if it should be a major, minor, or tiny release.
   This project uses [semantic versioning](https://semver.org/).
   While we haven't always strictly adhered to semver in the past, we should do our best moving forward.
   From the semver docs:
   > given a version number MAJOR.MINOR.PATCH, increment the:
   >
   > - MAJOR version when you make incompatible API changes,
   > - MINOR version when you add functionality in a backwards compatible manner, and
   > - PATCH version when you make backwards compatible bug fixes.
   >
2. Determine the current version.
   `git describe` helps, and if you are missing annotated tags use `git describe --tags`.
3. Determine the next version.
   If your version is `0.x.x` (MAJOR is 0), and you don't want to create a `1.x.x` release, shift the number semantics right, e.g. if your version is `0.2.5` and you make incompatible API changes, your next version is `0.3.0`.
    - If you're doing a pre-release, make sure to do it in a PyPI-compatible manner, as described in [PEP 440](https://www.python.org/dev/peps/pep-0440/#pre-releases).
4. Search the library for the new version identifier to see if anything has been marked for deprecation.
   If so, remove those items in a separate PR *before* opening the release PR.
5. Create a new branch named `release/vX.X.X`, e.g. `release/v0.3.0`.
6. If you're working in **stactools**, update [`src/stactools/core/__init__.py`](src/stactools/core/__init__.py) with your new version number.
   If you're in a package, update the appropriate `__init__.py` file.
7. Update [CHANGELOG.md](CHANGELOG.md):
   1. Change `[Unreleased]` to your new version number and add a date.
   2. Add a link to your new version at the bottom of the page, e.g. `[0.3.0]: <https://github.com/stac-utils/stactools/compare/v0.2.5..v0.3.0>`.
   3. Update the `[Unreleased]` link at the bottom of the page to start at your new release.
   4. Audit your new section of the CHANGELOG to ensure all relevant changes are captured.
8. Open a pull request for your branch.
   Include a "Release summary" section which includes the contents of your section of the CHANGELOG.
9. Once approved, merge the branch.
10. Create an **annotated** tag at the new **main** HEAD named `vX.X.X`, e.g. `v0.3.0`.
    - The contents of the tag should be the CHANGELOG contents for your version release.
      Be sure to remove any leading `###`, they'll be considered comments in the tag contents.
      See previous annotated tags for examples of formatting.
11. Push your tag.
    This will fire off a special [release Github action](.github/workflows/release.yml) that will push your package to PyPI.
12. Create a new release for your tag in the [Github releases](https://github.com/stac-utils/stactools/releases).

## FAQS

### Are stactools-packages versioned separately from the main command?

Yes, **stactools-packages** should follow their own release schedule, as their stability tied to **stactools** itself.

### Is there a roadmap for stac-utils 1.0?

Not at this time.
