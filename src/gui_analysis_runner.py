import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.gui.services import (
    DEFAULT_ICONICITY_CSV,
    DEFAULT_RATED_OUTPUT_DIR,
    DEFAULT_TOKENS_OUTPUT_DIR,
    DEFAULT_TYPE_COUNT_MODE,
    DEFAULT_TYPES_OUTPUT_DIR,
    TYPE_COUNT_ONLY_ONCE,
    TYPE_COUNT_WITH_REPETITIONS,
    run_rated_export,
    run_tokens_analysis,
    run_types_analysis,
)

_DEFAULT_PROCESSED_ROOT = {
    "tokens": "Corpora_modified",
    "types": "Corpora_modified",
    "rated": DEFAULT_TYPES_OUTPUT_DIR,
}

_DEFAULT_OUTPUT_DIR = {
    "tokens": DEFAULT_TOKENS_OUTPUT_DIR,
    "types": DEFAULT_TYPES_OUTPUT_DIR,
    "rated": DEFAULT_RATED_OUTPUT_DIR,
}

_DEFAULT_RESULT_FILE = {
    "tokens": "tokens_result.json",
    "types": "types_result.json",
    "rated": "rated_result.json",
}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Ejecuta analisis de la GUI con un interprete alternativo."
    )
    parser.add_argument("mode", choices=("tokens", "types", "rated"))
    parser.add_argument("--processed-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--iconicity-csv", default=DEFAULT_ICONICITY_CSV)
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
    parser.add_argument(
        "--type-count-mode",
        choices=(TYPE_COUNT_WITH_REPETITIONS, TYPE_COUNT_ONLY_ONCE),
        default=DEFAULT_TYPE_COUNT_MODE,
    )
    parser.add_argument("--result-file", default=None)
    args = parser.parse_args(argv)

    processed_root = args.processed_root or _DEFAULT_PROCESSED_ROOT[args.mode]
    output_dir = args.output_dir or _DEFAULT_OUTPUT_DIR[args.mode]
    result_file = args.result_file or _DEFAULT_RESULT_FILE[args.mode]

    selected_corpora = args.selected_corpora or []
    categories = args.categories or []
    print(
        "Runner de análisis iniciado:"
        f" mode={args.mode},"
        f" corpora={selected_corpora if selected_corpora else 'todos'},"
        f" plots={'si' if args.generate_plots else 'no'},"
        f" categories={categories if categories else 'todas'},"
        f" type_count_mode={args.type_count_mode}"
    )
    sys.stdout.flush()

    if args.mode == "rated":
        result = run_rated_export(
            source_dir=processed_root,
            output_dir=output_dir,
            iconicity_csv=args.iconicity_csv,
        )
    elif args.mode == "types":
        result = run_types_analysis(
            processed_root,
            selected_corpora=args.selected_corpora,
            categories=args.categories,
            output_dir=output_dir,
            iconicity_csv=args.iconicity_csv,
            generate_plots=args.generate_plots,
            plots_dir=args.plots_dir,
            plot_count_criteria=tuple(args.plot_count_criteria)
            if args.plot_count_criteria
            else None,
            type_count_mode=args.type_count_mode,
        )
    else:
        result = run_tokens_analysis(
            processed_root,
            selected_corpora=args.selected_corpora,
            output_dir=output_dir,
            iconicity_csv=args.iconicity_csv,
            generate_plots=args.generate_plots,
            plots_dir=args.plots_dir,
            distribution_dir=args.distribution_dir,
        )

    payload = {
        "outputs": result.get("outputs"),
        "plot_outputs": result.get("plot_outputs"),
    }
    with open(result_file, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
