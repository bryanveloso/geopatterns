# Changelog

## 0.1.0 (unreleased)

First release since 0.0.1. Gasp.

### Breaking
- Requires Python 3.11 or newer.
- The SVG output has changed for every pattern. It now matches geo_pattern 1.5.0 for the same string and options, so patterns generated with 0.0.1 will look different. Element attributes, sizes and the default background colour are all different.

### Added
- 7 patterns from upstream: `chevrons`, `concentric_circles`, `diamonds`, `mosaic_squares`, `nested_squares`, `octagons` and `tessellation`. There are now 16.
- `patterns=` takes a pattern name or a list of names. If you pass none, the hash picks one, so a pattern no longer has to be chosen.
- `color=` for an exact background colour and `base_color=` for a colour whose hue and saturation shift with the string.
- `InvalidPatternError`, a `ValueError` subclass, raised for an unknown pattern name.
- Tests: smoke and API tests, plus parity tests against upstream's 18 fixtures and 623 hashes generated from its Ruby code (`tests/ruby/generate_hashes.rb`).

### Changed
- Packaging moved from `setup.py` to `pyproject.toml`.
- `colour` is replaced by the standard library's `colorsys`.
- `SVG` is stringified with `str()` and no longer has a `to_string()` method.

### Deprecated
- `generator=`. Use `patterns=`; it warns with a `DeprecationWarning`.
- The old names `bricks`, `rings` and `sinewaves`. They still work through `generator=` and draw `octagons`, `concentric_circles` and `sine_waves`, with a warning that says so.

### Removed
- `setup.py`.
- The `colour` dependency.

### Fixed
- `base64_string` crashed on Python 3.9 and newer, because `base64.encodestring` is gone.
- `setup.py` raised a `NameError` (`setuptools` was never imported), so the 2021 `pip install` fix never worked.
- README: stale link to upstream, a bogus `u'...'` prefix in the example output, and a missing `BytesIO` import.

### Known differences from upstream
- `GeoPattern()` needs a string, and a non-string raises `AttributeError`. Upstream defaults to the current time and converts other types to strings.
