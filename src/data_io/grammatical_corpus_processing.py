from src.data_io.grammatical_formatter import GrammaticalDataFormatter


def process_grammatical_data_with_formatter(corpus_data):
    """
    Procesa los datos morfológicos usando GrammaticalDataFormatter,
    manteniendo la estructura jerárquica del corpus.
    """
    result = {"Corpus_modified": {}}

    for corpus_name in ["Brent", "NewEngland", "Post", "VanKleeck"]:
        if corpus_name not in corpus_data["Corpus_modified"]:
            continue

        result["Corpus_modified"][corpus_name] = {}
        corpus_data_current = corpus_data["Corpus_modified"][corpus_name]

        for dir_name, content in corpus_data_current.items():
            if "files" not in content:
                continue

            result["Corpus_modified"][corpus_name][dir_name] = {"files": []}

            for file in content["files"]:
                file_path = file["metadata"]["file_path"]
                if not file_path.endswith(".cha"):
                    continue

                formatter = GrammaticalDataFormatter()
                children_data, adults_data = formatter.format_cha_data_from(file_path)

                processed_file = {
                    "metadata": file["metadata"].copy(),
                    "children_data": children_data,
                    "adults_data": adults_data,
                }
                result["Corpus_modified"][corpus_name][dir_name]["files"].append(
                    processed_file
                )

    return result
