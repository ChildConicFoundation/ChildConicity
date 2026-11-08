"""Shared checks for whether an analysis can run."""

import importlib.util
import os
from pathlib import Path

from src.data_io.corpus_selection import CORPUS_DATA_ROOT_KEY, discover_available_corpora


PANDAS_MODULE = "pandas"
PLOT_MODULES = ("matplotlib", "numpy", "seaborn")


def missing_modules(module_names):
    return [
        name
        for name in module_names
        if importlib.util.find_spec(name) is None
    ]


def required_analysis_modules(mode, generate_plots):
    if mode == "tokens":
        modules = [PANDAS_MODULE]
        if generate_plots:
            modules.extend(PLOT_MODULES)
        return modules

    if mode == "types" and generate_plots:
        return [PANDAS_MODULE, *PLOT_MODULES]

    return []


def ratings_file_ready(path):
    return os.path.isfile(path)


def inspect_processed_corpora(processed_root):
    exists = bool(processed_root) and os.path.isdir(processed_root)
    folder_name = (
        os.path.basename(os.path.normpath(processed_root)) if processed_root else ""
    )
    corpora = discover_available_corpora(processed_root) if exists else []
    return {
        "exists": exists,
        "name_ok": folder_name == CORPUS_DATA_ROOT_KEY,
        "corpora": corpora,
        "ready": exists and bool(corpora),
    }


def missing_selected_corpora(processed_root, selected_corpora, available_corpora):
    return [
        corpus_name
        for corpus_name in selected_corpora
        if corpus_name not in available_corpora
        or not os.path.isdir(os.path.join(processed_root, corpus_name))
    ]


def rated_source_ready(source):
    if not source or not os.path.isdir(source):
        return False

    return any(
        (child / "WordCount").is_dir()
        for child in Path(source).iterdir()
        if child.is_dir()
    )
