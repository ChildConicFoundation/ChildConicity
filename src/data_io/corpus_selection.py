import os


def discover_available_corpora(processed_root):
    if not os.path.isdir(processed_root):
        return []

    return sorted(
        item
        for item in os.listdir(processed_root)
        if os.path.isdir(os.path.join(processed_root, item))
    )


def filter_corpus_data(corpus_data, selected_corpora=None):
    if selected_corpora is None:
        return corpus_data

    corpus_root = corpus_data.get("Corpus_modified", {})
    filtered_root = {
        corpus_name: corpus_root[corpus_name]
        for corpus_name in selected_corpora
        if corpus_name in corpus_root
    }

    return {"Corpus_modified": filtered_root}
