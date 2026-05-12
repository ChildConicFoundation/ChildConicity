import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.quarterly_samples.rated_exporter import export_rated


def main():
    export_rated(
        source_root="quarterly_grammatical_categories",
        output_root="rated_quarterly_grammatical_categories",
        iconicity_csv="iconicity_ratings_cleaned.csv",
    )
    print("Exportación completada.")


if __name__ == "__main__":
    raise SystemExit(main())
