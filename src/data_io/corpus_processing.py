from src.data_io.corpus_selection import (
    CORPUS_DATA_ROOT_KEY,
    TARGET_CORPORA,
    require_corpus_data_root,
)
from src.data_io.data_formatter import DataFormatter


def process_data_with_formatter(corpus_data):
    """
    Processes data using DataFormatter to separate child and adult data,
    preserving the corpus hierarchy.
    """
    corpus_data = require_corpus_data_root(corpus_data)
    result = {CORPUS_DATA_ROOT_KEY: {}}
    corpus_root = corpus_data.get(CORPUS_DATA_ROOT_KEY, {})

    for corpus_name in TARGET_CORPORA:
        if corpus_name not in corpus_root:
            continue

        result[CORPUS_DATA_ROOT_KEY][corpus_name] = {}
        corpus_data_current = corpus_root[corpus_name]

        for dir_name, content in corpus_data_current.items():
            if "files" not in content:
                continue

            result[CORPUS_DATA_ROOT_KEY][corpus_name][dir_name] = {"files": []}

            for file in content["files"]:
                file_path = file["metadata"]["file_path"]
                if not file_path.endswith(".cha"):
                    continue

                formatter = DataFormatter()
                (
                    children_data,
                    other_children_data,
                    adults_data,
                ) = formatter.format_cha_data_from(file_path)

                processed_file = {
                    "metadata": file["metadata"].copy(),
                    "children_data": children_data,
                    "other_children_data": other_children_data,
                    "adults_data": adults_data,
                }
                result[CORPUS_DATA_ROOT_KEY][corpus_name][dir_name]["files"].append(
                    processed_file
                )

    return result
