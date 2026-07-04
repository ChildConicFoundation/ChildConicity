import os

CORPUS_DATA_ROOT_KEY = "Corpora_modified"
TARGET_CORPORA = (
    "Bates",
    "Brent",
    "NewEngland",
    "Post",
    "Bloom",
    "Brown",
    "HSLLD",
    "Kuczaj",
    "Sachs",
    "VanKleeck",
    "Providence",
)


def require_corpus_data_root(corpus_data):
    """
    Ensures corpus data uses the canonical root key expected by the pipeline.
    """
    if not isinstance(corpus_data, dict) or CORPUS_DATA_ROOT_KEY not in corpus_data:
        raise ValueError(f"Corpus data must contain a '{CORPUS_DATA_ROOT_KEY}' root.")

    return corpus_data


def require_corpus_data_root_path(processed_root):
    if os.path.basename(os.path.normpath(processed_root)) != CORPUS_DATA_ROOT_KEY:
        raise ValueError(f"Processed root must be named '{CORPUS_DATA_ROOT_KEY}'.")


def discover_available_corpora(processed_root):
    if not os.path.isdir(processed_root):
        return []

    return sorted(
        item
        for item in os.listdir(processed_root)
        if os.path.isdir(os.path.join(processed_root, item))
    )


def filter_corpus_data(corpus_data, selected_corpora=None):
    corpus_data = require_corpus_data_root(corpus_data)
    if selected_corpora is None:
        return corpus_data
    corpus_root = corpus_data.get(CORPUS_DATA_ROOT_KEY, {})
    filtered_root = {
        corpus_name: corpus_root[corpus_name]
        for corpus_name in selected_corpora
        if corpus_name in corpus_root
    }

    return {CORPUS_DATA_ROOT_KEY: filtered_root}
