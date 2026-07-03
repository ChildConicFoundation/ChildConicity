from src.data_io.grammatical_formatter import GrammaticalDataFormatter

TARGET_CORPORA = ("Brent", "NewEngland", "Post", "Bloom", "Brown", "HSLLD", "Kuczaj", "Sachs", "VanKleeck")


def process_grammatical_data_with_formatter(
    corpus_data, grammatical_categories=None
):
    """
    Processes morphological data using GrammaticalDataFormatter,
    preserving the corpus hierarchy.
    """
    result = {"Corpora_modified": {}}
    formatter = GrammaticalDataFormatter(grammatical_categories=grammatical_categories)

    for corpus_name, corpus_data_current in _iter_target_corpora(corpus_data):
        processed_corpus = _process_corpus_directories(corpus_data_current, formatter)
        if processed_corpus:
            result["Corpora_modified"][corpus_name] = processed_corpus

    return result


def run_grammatical_pipeline(
    corpus_data, output_dir, grammatical_categories=None, exporter_class=None
):
    from src.quarterly_samples import (
        GrammaticalCategoriesExporter,
        group_data_by_age,
    )

    if exporter_class is None:
        exporter_class = GrammaticalCategoriesExporter

    processed_data = process_grammatical_data_with_formatter(
        corpus_data,
        grammatical_categories=grammatical_categories,
    )
    grouped_data = group_data_by_age(processed_data)
    outputs = exporter_class(output_dir).export(grouped_data)

    return {
        "processed_data": processed_data,
        "grouped_data": grouped_data,
        "outputs": outputs,
    }


def collect_grammatical_categories(corpus_data):
    categories = set()

    for file in _iter_corpus_files(corpus_data.get("Corpora_modified", {})):
        utterances = file.get("metadata", {}).get("morphological_utterances", [])
        for utterance in utterances:
            for token in utterance.get("tokens", []):
                category = token.get("category")
                if category:
                    categories.add(category)

    return sorted(categories)


def _iter_corpus_files(content):
    if isinstance(content, dict):
        files = content.get("files", [])
        for file in files:
            yield file

        for key, value in content.items():
            if key != "files":
                yield from _iter_corpus_files(value)


def _iter_target_corpora(corpus_data):
    corpus_root = corpus_data.get("Corpora_modified", {})
    for corpus_name in TARGET_CORPORA:
        if corpus_name in corpus_root:
            yield corpus_name, corpus_root[corpus_name]


def _process_corpus_directories(corpus_data_current, formatter):
    processed_corpus = {}

    for dir_name, content in corpus_data_current.items():
        processed_directory = _process_directory_files(content, formatter)
        if processed_directory is not None:
            processed_corpus[dir_name] = processed_directory

    return processed_corpus


def _process_directory_files(content, formatter):
    if "files" not in content:
        return None

    processed_files = []
    for file in content["files"]:
        processed_file = _process_file(file, formatter)
        if processed_file is not None:
            processed_files.append(processed_file)

    return {"files": processed_files}


def _process_file(file, formatter):
    file_path = file["metadata"]["file_path"]
    if not file_path.endswith(".cha"):
        return None

    children_data, other_children_data, adults_data = formatter.format_cha_data_from(
        file_path
    )
    if children_data is None:
        return None

    metadata = file["metadata"].copy()
    metadata["mlu_stats"] = formatter.last_mlu_stats

    return {
        "metadata": metadata,
        "children_data": children_data,
        "other_children_data": other_children_data,
        "adults_data": adults_data,
    }
