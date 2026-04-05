from src.data_io.corpus_selection import (
    discover_available_corpora,
    filter_corpus_data,
)


def test_discover_available_corpora_lists_only_directories(tmp_path):
    processed_root = tmp_path / "Corpus_modified"
    processed_root.mkdir()
    (processed_root / "Brent").mkdir()
    (processed_root / "Post").mkdir()
    (processed_root / "README.txt").write_text("hola", encoding="utf-8")

    assert discover_available_corpora(str(processed_root)) == ["Brent", "Post"]


def test_filter_corpus_data_keeps_only_selected_corpora():
    corpus_data = {
        "Corpus_modified": {
            "Brent": {"a": {}},
            "Post": {"b": {}},
            "VanKleeck": {"c": {}},
        }
    }

    filtered_data = filter_corpus_data(corpus_data, ["Post", "VanKleeck"])

    assert filtered_data == {
        "Corpus_modified": {
            "Post": {"b": {}},
            "VanKleeck": {"c": {}},
        }
    }


def test_filter_corpus_data_returns_original_data_for_all():
    corpus_data = {"Corpus_modified": {"Brent": {"a": {}}}}

    assert filter_corpus_data(corpus_data, None) == corpus_data
