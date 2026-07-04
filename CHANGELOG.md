# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.0.0]: https://github.com/ChildConicFoundation/ChildConicity/releases/tag/v1.0.0
