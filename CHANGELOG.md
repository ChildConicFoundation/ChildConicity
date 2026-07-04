# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6] - 2026-07-05

### Changed

- Align author metadata with Zenodo: Iban Rodriguez Iglesias (alias Errowdrigorena) in `CITATION.cff`, `.zenodo.json`, and package metadata.

## [1.0.5] - 2026-07-05

### Fixed

- Simplify `.zenodo.json` metadata (creators, license, remove conflicting fields) so GitHub releases can be archived on Zenodo.

## [1.0.4] - 2026-07-05

### Fixed

- Use Zenodo's `bsl-1.0` license identifier in `.zenodo.json` so archived GitHub releases can be deposited with the correct license metadata.

## [1.0.3] - 2026-07-04

### Added

- Zenodo metadata file for archived GitHub releases.

## [1.0.2] - 2026-07-04

### Added

- Corpus-specific citation guidance for all supported CHILDES/TalkBank corpora in the English and Spanish README files.

## [1.0.1] - 2026-07-04

### Added

- `CITATION.cff` for the GitHub **Cite this repository** button.
- Citation section in README (English and Spanish) with BibTeX and APA examples.

## [1.0.0] - 2026-07-04

First stable release of ChildConicity.

### Added

- Tkinter GUI with English and Spanish interface (`examples/gui.py`).
- Command-line tools for corpus download, iconicity ratings download, and analysis.
- Normalization pipeline for 11 CHILDES/TalkBank corpora: Bates, Bloom, Brent, Brown, HSLLD, Kuczaj, NewEngland, Post, Providence, Sachs, and VanKleeck.
- Quarterly sample analysis in three modes: `tokens`, `types`, and `rated`.
- Iconicity matching against an external ratings database (OSF).
- Plot generation for token and type analyses.
- Machine-readable JSON summaries via `gui_analysis_runner.py` (`--result-file`).
- TalkBank credential support through environment variables (`CHILDCONICITY_TALKBANK_USER`, `CHILDCONICITY_TALKBANK_PASSWORD`).
- Automated test suite with ≥80% code coverage enforced in CI.

### Documentation

- README in English and Spanish with GUI workflow, CLI reference, and agent/automation guide.

### Known limitations

- TalkBank corpus download depends on Selenium and a Chrome/Chromedriver session.
- Iconicity ratings and corpora are not bundled; they must be downloaded separately.
- Long analyses report progress on stdout only; there is no streaming progress API.
- GUI and visualization modules are excluded from the coverage threshold.

[1.0.6]: https://github.com/ChildConicFoundation/ChildConicity/releases/tag/v1.0.6
[1.0.5]: https://github.com/ChildConicFoundation/ChildConicity/releases/tag/v1.0.5
[1.0.4]: https://github.com/ChildConicFoundation/ChildConicity/releases/tag/v1.0.4
[1.0.3]: https://github.com/ChildConicFoundation/ChildConicity/releases/tag/v1.0.3
[1.0.2]: https://github.com/ChildConicFoundation/ChildConicity/releases/tag/v1.0.2
[1.0.1]: https://github.com/ChildConicFoundation/ChildConicity/releases/tag/v1.0.1
[1.0.0]: https://github.com/ChildConicFoundation/ChildConicity/releases/tag/v1.0.0
