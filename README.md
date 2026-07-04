# ChildConicity

[![Python Tests](https://github.com/errowdrigorena/ChildConicity/actions/workflows/python-tests.yml/badge.svg)](https://github.com/errowdrigorena/ChildConicity/actions/workflows/python-tests.yml)

🇬🇧 English | [🇪🇸 Español](README.es.md)

ChildConicity processes CHILDES/TalkBank corpora and analyzes iconicity in child language development. It normalizes `.cha` transcripts, groups data by age in quarterly samples, and exports results for tokens, grammatical categories, and iconicity ratings.

## Installation

A virtual environment is recommended:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To download corpora from TalkBank, you need a TalkBank account and Chrome/Chromedriver available, because authentication is handled with Selenium.

## Recommended Use: GUI

The easiest way to use the project is through the GUI:

```bash
source .venv/bin/activate
python3 examples/gui.py
```

In the main window:

0. Choose **Language** (`English` / `Español`) at the top. The choice is saved in `.childconicity_locale` (or override with `CHILDCONICITY_LOCALE=en|es`).
1. If you do not have local corpora yet, enter your TalkBank email and password and click `Download corpora`. By default, corpora are downloaded to `Corpora/`.
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

Useful options:

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
- `--force`: overwrite the CSV if it already exists.

### Initialize Corpora

```bash
source .venv/bin/activate
python3 examples/initialize_corpuses.py
```

By default, this reads from `Corpora/` and writes to `Corpora_modified/`.

The included normalizers process these corpora: `Bates`, `Bloom`, `Brent`, `Brown`, `HSLLD`, `Kuczaj`, `NewEngland`, `Post`, `Providence`, `Sachs`, and `VanKleeck`.

### Run Analyses

The analysis runner is:

```bash
source .venv/bin/activate
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --generate-plots
python3 src/gui_analysis_runner.py types --processed-root Corpora_modified --generate-plots
python3 src/gui_analysis_runner.py rated --processed-root quarterly_grammatical_categories
```

Useful options:

- `--corpus NAME`: filter by corpus; can be repeated.
- `--category CATEGORY`: filter grammatical categories in `types` mode; can be repeated.
- `--output-dir DIR`: change the output folder.
- `--iconicity-csv FILE`: use another ratings CSV.
- `--result-file FILE`: change the runner summary JSON.
- `--type-count-mode with_repetitions|only_once`: change how types are counted in plots.

Examples:

```bash
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --corpus Brent --corpus Post
python3 src/gui_analysis_runner.py types --processed-root Corpora_modified --category noun --category verb --generate-plots
python3 src/gui_analysis_runner.py rated --processed-root quarterly_grammatical_categories --output-dir rated_quarterly_grammatical_categories
```

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
