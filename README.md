# ChildConicity

[![CI](https://github.com/ChildConicFoundation/ChildConicity/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/ChildConicFoundation/ChildConicity/actions/workflows/python-tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-≥80%25-04e762?logo=pytest&logoColor=white)](https://github.com/ChildConicFoundation/ChildConicity#tests)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: BSL-1.0](https://img.shields.io/badge/License-BSL--1.0-0052CC)](LICENSE)

[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-555)](#installation)
[![Corpus](https://img.shields.io/badge/corpus-CHILDES%20%2F%20TalkBank-8B4513)](https://talkbank.org/childes/)
[![Iconicity ratings](https://img.shields.io/badge/iconicity-OSF-orange)](https://osf.io/ex37k/)
[![GUI](https://img.shields.io/badge/interface-Tkinter%20GUI-FF6F00)](#recommended-use-gui)
[![CLI](https://img.shields.io/badge/automation-CLI%20%7C%20agents-2ea44f)](#automation-and-ai-agent-integration)
[![Languages](https://img.shields.io/badge/languages-en%20%7C%20es-007ec6)](README.es.md)
[![Last commit](https://img.shields.io/github/last-commit/ChildConicFoundation/ChildConicity)](https://github.com/ChildConicFoundation/ChildConicity/commits/main)
[![Issues](https://img.shields.io/github/issues/ChildConicFoundation/ChildConicity)](https://github.com/ChildConicFoundation/ChildConicity/issues)

🇬🇧 English | [🇪🇸 Español](README.es.md)

ChildConicity processes CHILDES/TalkBank corpora and analyzes iconicity in child language development. It normalizes `.cha` transcripts, groups data by age in quarterly samples, and exports results for tokens, grammatical categories, and iconicity ratings.

## Installation

A virtual environment is recommended:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# or: pip install -e ".[dev]"   # editable install with test dependencies
```

To download corpora from TalkBank, you need a TalkBank account and Chrome/Chromedriver available, because authentication is handled with Selenium.

Before running any analysis, you also need the iconicity ratings database at `iconicity_ratings/iconicity_ratings_cleaned.csv`. It is not included in the repository. Download it from the GUI (**Download iconicity ratings**) or from the terminal with `python3 -m src.cli.download_iconicity_ratings` (fetched from OSF; no account required).

## Recommended Use: GUI

The easiest way to use the project is through the GUI:

```bash
source .venv/bin/activate
python3 examples/gui.py
```

In the main window:

0. Choose **Language** (`English` / `Español`) at the top. The choice is saved in `.childconicity_locale` (or override with `CHILDCONICITY_LOCALE=en|es`).
1. In the **Downloads** section, fetch the data you need:
   - **Download corpora**: requires TalkBank email and password; saves to `Corpora/`.
   - **Download iconicity ratings**: downloads the iconicity database from OSF to `iconicity_ratings/iconicity_ratings_cleaned.csv` (required for all analyses).
2. Check the paths:
   - `Source corpus`: folder with the original corpora, usually `Corpora/`.
   - `Processed corpus`: normalized output folder, usually `Corpora_modified/`.
3. Click `Initialize corpora` to transform the original corpora into the format used by the analyses.
4. Click `Show initialized corpora` to load the list of available corpora.
5. Select `All corpora` or choose specific corpora.
6. Choose a mode:
   - `Tokens`: analysis of iconic and non-iconic words by quarter.
   - `Types`: grammatical category analysis.
7. Click `Run analysis` to export data or `Generate plots` to create visualizations.
8. For `Rated`, run `Types` first; then use the iconicity export section to generate `WordCount` with ratings and `LemaCount`.

Default output directories:

- `quarterly_valid_words/`: token analysis results.
- `quarterly_grammatical_categories/`: type analysis results.
- `rated_quarterly_grammatical_categories/`: results enriched with iconicity ratings.
- `iconic_vs_noniconic/` and `distribution/`: token plots generated from the command line when no custom paths are provided.
- In the GUI, token plots are saved inside the selected output directory, under `iconic_vs_noniconic/` and `distribution/`.

## Command-Line Usage

The GUI internally calls the same services that can be run from the terminal.

### Download Corpora

```bash
source .venv/bin/activate
python3 -m src.cli.download_corpora --user your@email --password your_password --corpora Brent Bloom
```

For scripts and agents, prefer environment variables so credentials do not appear in shell history:

```bash
export CHILDCONICITY_TALKBANK_USER=your@email
export CHILDCONICITY_TALKBANK_PASSWORD=your_password
python3 -m src.cli.download_corpora --corpora Brent Bloom
```

CLI flags override environment variables when both are provided.

Useful options:

- `--user EMAIL`: TalkBank email. Defaults to `CHILDCONICITY_TALKBANK_USER`.
- `--password PASSWORD`: TalkBank password. Defaults to `CHILDCONICITY_TALKBANK_PASSWORD`.
- `--corpora Brent Bloom`: download only those corpora. If omitted, the command tries to download all corpora.
- `--output-dir Corpora`: change the target folder.
- `--force`: overwrite existing corpora.
- `--no-headless`: show the browser during login.

### Download Iconicity Ratings

Iconicity analyses use `iconicity_ratings/iconicity_ratings_cleaned.csv`.
If you do not have it, or want to download it again from OSF:

```bash
source .venv/bin/activate
python3 -m src.cli.download_iconicity_ratings
```

Useful options:

- `--output FILE`: change the destination path.
- `--url URL`: change the OSF download URL.
- `--force`: overwrite the CSV if it already exists.

### Initialize Corpora

```bash
source .venv/bin/activate
python3 examples/initialize_corpuses.py
python3 examples/initialize_corpuses.py --source-root Corpora --output-root Corpora_modified
```

By default, this reads from `Corpora/` and writes to `Corpora_modified/`.

Useful options:

- `--source-root DIR`: folder with original corpora.
- `--output-root DIR`: folder for normalized corpora.

The included normalizers process these corpora: `Bates`, `Bloom`, `Brent`, `Brown`, `HSLLD`, `Kuczaj`, `NewEngland`, `Post`, `Providence`, `Sachs`, and `VanKleeck`.

### Run Analyses

The analysis runner is the same entry point used by the GUI in a subprocess:

```bash
source .venv/bin/activate
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --generate-plots
python3 src/gui_analysis_runner.py types --processed-root Corpora_modified --generate-plots
python3 src/gui_analysis_runner.py rated --processed-root quarterly_grammatical_categories
```

Modes:

- `tokens`: iconic and non-iconic word counts by quarter.
- `types`: grammatical category export. Required before `rated`.
- `rated`: enriches the `types` output with iconicity ratings (`WordCount` with ratings and `LemaCount`).

Useful options:

- `--corpus NAME`: filter by corpus; can be repeated.
- `--category CATEGORY`: filter grammatical categories in `types` mode; can be repeated.
- `--output-dir DIR`: change the output folder.
- `--iconicity-csv FILE`: use another ratings CSV.
- `--generate-plots`: create PNG visualizations.
- `--plots-dir DIR`: token or type plot folder (`tokens` and `types` modes).
- `--distribution-dir DIR`: cumulative distribution plots for `tokens` mode.
- `--plot-count-criteria GROUP`: speaker groups for type plots (`adults`, `children`, ...); can be repeated.
- `--result-file FILE`: write a machine-readable summary JSON (see below).
- `--type-count-mode with_repetitions|only_once`: change how types are counted in plots.

Default summary files if `--result-file` is omitted: `tokens_result.json`, `types_result.json`, and `rated_result.json` in the project root. These are execution artifacts and are ignored by git (`*_result.json`).

Examples:

```bash
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --corpus Brent --corpus Post
python3 src/gui_analysis_runner.py types --processed-root Corpora_modified --category noun --category verb --generate-plots
python3 src/gui_analysis_runner.py rated --processed-root quarterly_grammatical_categories --output-dir rated_quarterly_grammatical_categories
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --generate-plots \
  --plots-dir quarterly_valid_words/iconic_vs_noniconic \
  --distribution-dir quarterly_valid_words/distribution \
  --result-file /tmp/tokens_result.json
```

#### Runner summary JSON

When the analysis finishes, the runner writes a JSON file with the paths it generated. This is the main machine-readable contract for scripts and agents:

```json
{
  "outputs": { "...": "..." },
  "plot_outputs": { "...": "..." }
}
```

- `outputs`: export paths from the analysis step. In `tokens` and `types` modes this is a nested map of generated JSON/CSV files. In `rated` mode it contains `source_dir` and `output_dir`.
- `plot_outputs`: present only when `--generate-plots` is used. Includes `plots_dir`, optional `distribution_dir`, and a `files` map with PNG paths.

The GUI uses the same runner with a temporary `--result-file` and then reads this JSON to show the generated files.

## Automation and AI Agent Integration

For scripts, CI jobs, or AI agents, prefer the command line over the Tkinter GUI. The GUI does not add analysis logic: it launches `src/gui_analysis_runner.py` in a subprocess with the same services documented above.

### Recommended pipeline

Run these steps from the project root with the virtual environment activated:

```bash
python3 -m src.cli.download_iconicity_ratings
python3 examples/initialize_corpuses.py --source-root Corpora --output-root Corpora_modified
python3 src/gui_analysis_runner.py types --processed-root Corpora_modified --result-file /tmp/types_result.json
python3 src/gui_analysis_runner.py rated \
  --processed-root quarterly_grammatical_categories \
  --output-dir rated_quarterly_grammatical_categories \
  --result-file /tmp/rated_result.json
```

Optional token analysis:

```bash
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --result-file /tmp/tokens_result.json
```

### Why the CLI works well for agents

- **Composable steps**: each command has a single responsibility and clear inputs/outputs.
- **Parity with the GUI**: agents get the same behavior as the graphical interface.
- **Structured completion data**: pass `--result-file` and parse the JSON instead of guessing output paths.
- **Scoped runs**: `--corpus` and `--category` reduce runtime during iteration.
- **Idempotent downloads**: ratings and corpora are skipped when already present unless `--force` is used.
- **Headless by default**: all analysis steps run without a display. Only TalkBank corpus download needs Chrome/Selenium.

### Preconditions an agent should verify

1. `iconicity_ratings/iconicity_ratings_cleaned.csv` exists.
2. `Corpora_modified/` exists and contains the corpora to analyze.
3. For `rated`, `quarterly_grammatical_categories/` must already exist from a prior `types` run.
4. For plots, `matplotlib`, `numpy`, and `seaborn` must be installed (already listed in `requirements.txt`).

### Security and operational notes

- Prefer `CHILDCONICITY_TALKBANK_USER` and `CHILDCONICITY_TALKBANK_PASSWORD` for TalkBank credentials instead of `--user` / `--password` on the command line.
- TalkBank download is the most fragile automation step because it depends on Selenium and a real browser session.
- Long runs only report progress on stdout; there is no streaming progress API yet.
- `*_result.json` files are local execution artifacts. Do not treat them as project inputs or commit them.

## What Does the Analysis Do?

The program:

1. Reads normalized corpora from `Corpora_modified/`.
2. Groups data by age in quarterly samples.
3. Separates adult, child, and, when applicable, other-child productions.
4. Matches words or lemmas against `iconicity_ratings/iconicity_ratings_cleaned.csv`.
5. Exports JSON/CSV files with statistics by quarter.
6. Generates iconicity distribution plots when requested.

## Tests

To run tests and generate the coverage report:

```bash
source .venv/bin/activate
./run_tests.sh
```

The script:

- Runs all tests.
- Generates an HTML coverage report.
- Checks that coverage is above 80%.
- Saves the report in `coverage_report/htmlcov/`.

The GitHub Actions pipeline runs the tests and publishes the `coverage-report` artifact with the coverage report.

## Important Notes

- `iconicity_ratings/iconicity_ratings_cleaned.csv` can be downloaded from the GUI or with `python3 -m src.cli.download_iconicity_ratings`.
- Execution can take several minutes when many corpora are processed.
- The project generates multiple output files in JSON, CSV, and PNG.
- The current folder names are `Corpora/` and `Corpora_modified/`.
- Runner summary files (`*_result.json`) are generated locally and ignored by git.
- Type plots are saved under subfolders inside the selected output directory, for example `plots_count_criteria_all/`.
- In `tokens` mode, if you do not pass `--plots-dir` and `--distribution-dir`, plots are written to `iconic_vs_noniconic/` and `distribution/` at the project root. The GUI instead places them inside the selected output directory.
