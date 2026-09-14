# Contributing to ChildConicity

🇬🇧 English | [🇪🇸 Español](CONTRIBUTING.es.md)

Thank you for contributing. ChildConicity is citable research software: contributions land on `develop`, and `main` stays as the published line.

## Branching

1. Start from **`develop`**, not `main`.
2. Create a branch from there (`fix/...`, `feat/...`, or another short name).
3. Open a pull request **against `develop`**.
4. A maintainer reviews the PR. CI must pass on Python 3.10, 3.11, and 3.12. Then we merge to `develop`.

Do not open pull requests against `main`. Releases are merged from `develop` to `main` by maintainers.

```bash
git clone https://github.com/ChildConicFoundation/ChildConicity.git
cd ChildConicity
git checkout develop
git pull
git checkout -b fix/short-description
```

If you work from a fork, still branch from `develop` and open the PR with base `develop`.

## Setup and tests

Follow the [README](README.md) for installation. Then:

```bash
source .venv/bin/activate
pip install -e ".[dev]"
./run_tests.sh
```

CI runs on every branch push and on pull requests. Locally, keep coverage at **80% or above**.

Do not commit corpora, iconicity ratings, generated plots, or `*_result.json` files. Those stay local.

## What to send

Useful pull requests include bug fixes, tests, documentation, and new or improved corpus normalizers.

Open an issue first if the change is large or changes analysis results. Do not bump the package version, edit release metadata, or create tags; maintainers handle releases.

## AI-assisted contributions

AI tools are welcome. A human still has to review the change, understand it, and confirm it behaves as intended before opening the pull request. Passing CI is not a substitute for that review. You are responsible for the patch you submit, including any AI-generated parts.

## License

By contributing, you agree that your work is included under the [Boost Software License 1.0](LICENSE).
