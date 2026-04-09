import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.gui.services import run_tokens_analysis, run_types_analysis


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Ejecuta analisis de la GUI con un interprete alternativo."
    )
    parser.add_argument("mode", choices=("tokens", "types"))
    parser.add_argument("--processed-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--iconicity-csv", default="iconicity_ratings_cleaned.csv")
    parser.add_argument("--plots-dir")
    parser.add_argument("--distribution-dir")
    parser.add_argument("--generate-plots", action="store_true")
    parser.add_argument("--corpus", action="append", dest="selected_corpora")
    parser.add_argument("--category", action="append", dest="categories")
    parser.add_argument(
        "--plot-count-criteria",
        action="append",
        dest="plot_count_criteria",
    )
    parser.add_argument("--result-file", required=True)
    args = parser.parse_args(argv)

    selected_corpora = args.selected_corpora or []
    categories = args.categories or []
    print(
        "Runner de análisis iniciado:"
        f" mode={args.mode},"
        f" corpora={selected_corpora if selected_corpora else 'todos'},"
        f" plots={'si' if args.generate_plots else 'no'},"
        f" categories={categories if categories else 'todas'}"
    )
    sys.stdout.flush()

    if args.mode == "types":
        result = run_types_analysis(
            args.processed_root,
            selected_corpora=args.selected_corpora,
            categories=args.categories,
            output_dir=args.output_dir,
            iconicity_csv=args.iconicity_csv,
            generate_plots=args.generate_plots,
            plots_dir=args.plots_dir,
            plot_count_criteria=tuple(args.plot_count_criteria)
            if args.plot_count_criteria
            else None,
        )
    else:
        result = run_tokens_analysis(
            args.processed_root,
            selected_corpora=args.selected_corpora,
            output_dir=args.output_dir,
            iconicity_csv=args.iconicity_csv,
            generate_plots=args.generate_plots,
            plots_dir=args.plots_dir,
            distribution_dir=args.distribution_dir,
        )

    payload = {
        "outputs": result.get("outputs"),
        "plot_outputs": result.get("plot_outputs"),
    }
    with open(args.result_file, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
