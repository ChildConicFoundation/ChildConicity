"""Checks an agent should run before starting an analysis."""

import os

from src.analysis.shared_preconditions import (
    PLOT_MODULES,
    inspect_processed_corpora,
    missing_modules,
    rated_source_ready,
    ratings_file_ready,
)
from src.corpus_initialization import DEFAULT_OUTPUT_ROOT
from src.gui.services import DEFAULT_ICONICITY_CSV, DEFAULT_TYPES_OUTPUT_DIR


def check_preconditions(project_root="."):
    """Report whether the default analysis inputs are present.

    The checks follow the agent preconditions in the project README.
    Rated data uses the same WordCount rule as the GUI.
    """
    root = os.path.abspath(project_root)
    ratings_path = os.path.join(root, DEFAULT_ICONICITY_CSV)
    processed_root = os.path.join(root, DEFAULT_OUTPUT_ROOT)
    grammatical_dir = os.path.join(root, DEFAULT_TYPES_OUTPUT_DIR)

    ratings_ok = ratings_file_ready(ratings_path)
    processed = inspect_processed_corpora(processed_root)
    grammatical_ok = rated_source_ready(grammatical_dir)
    missing_plot_dependencies = missing_modules(PLOT_MODULES)
    plots_ok = not missing_plot_dependencies

    return {
        "project_root": root,
        "checks": {
            "iconicity_ratings": {
                "ok": ratings_ok,
                "path": ratings_path,
            },
            "processed_corpora": {
                "ok": processed["ready"],
                "path": processed_root,
                "corpora": processed["corpora"],
            },
            "grammatical_categories": {
                "ok": grammatical_ok,
                "path": grammatical_dir,
            },
            "plot_dependencies": {
                "ok": plots_ok,
                "missing": missing_plot_dependencies,
            },
        },
        "ready_for": {
            "tokens": ratings_ok and processed["ready"],
            "types": ratings_ok and processed["ready"],
            "rated": ratings_ok and grammatical_ok,
            "plots": plots_ok,
        },
    }
