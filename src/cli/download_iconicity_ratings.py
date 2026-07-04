import argparse
import csv
import os
from pathlib import Path

import requests


DEFAULT_ICONICITY_RATINGS_URL = "https://osf.io/ex37k/download"
DEFAULT_OUTPUT_PATH = "iconicity_ratings/iconicity_ratings_cleaned.csv"
REQUIRED_COLUMNS = {
    "word",
    "n_ratings",
    "n",
    "prop_known",
    "rating",
    "rating_sd",
}


def _validate_iconicity_csv(path):
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        columns = set(reader.fieldnames or [])

    missing = REQUIRED_COLUMNS - columns
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(
            "The downloaded file does not appear to be the expected iconicity CSV. "
            f"Missing columns: {missing_columns}."
        )


def download_iconicity_ratings(
    output_path=DEFAULT_OUTPUT_PATH,
    url=DEFAULT_ICONICITY_RATINGS_URL,
    force=False,
    session=None,
):
    output_path = Path(output_path)
    if output_path.exists() and not force:
        print(f"{output_path} already exists, skipping (use --force to overwrite).")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_name(f"{output_path.name}.tmp")
    http = session or requests.Session()

    try:
        with http.get(url, stream=True, timeout=(20, 60)) as response:
            response.raise_for_status()

            with open(temp_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        file.write(chunk)

        _validate_iconicity_csv(temp_path)
        os.replace(temp_path, output_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    print(f"Iconicity ratings downloaded to {output_path}.")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Download iconicity_ratings_cleaned.csv from OSF for iconicity analyses."
        )
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PATH,
        help=f"Destination path (default: {DEFAULT_OUTPUT_PATH}).",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_ICONICITY_RATINGS_URL,
        help="OSF download URL.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the file if it already exists.",
    )

    args = parser.parse_args(argv)
    download_iconicity_ratings(
        output_path=args.output,
        url=args.url,
        force=args.force,
    )


if __name__ == "__main__":
    main()
