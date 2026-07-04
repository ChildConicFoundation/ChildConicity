import pytest

from src.data_io.corpus_selection import (
    CORPUS_DATA_ROOT_KEY,
    TARGET_CORPORA,
    discover_available_corpora,
    filter_corpus_data,
    require_corpus_data_root,
)


def test_discover_available_corpora_lists_only_directories(tmp_path):
    processed_root = tmp_path / "Corpora_modified"
    processed_root.mkdir()
    (processed_root / "Brent").mkdir()
    (processed_root / "Post").mkdir()
    (processed_root / "README.txt").write_text("hola", encoding="utf-8")

    assert discover_available_corpora(str(processed_root)) == ["Brent", "Post"]


def test_filter_corpus_data_keeps_only_selected_corpora():
    corpus_data = {
        "Corpora_modified": {
            "Brent": {"a": {}},
            "Post": {"b": {}},
            "VanKleeck": {"c": {}},
        }
    }

    filtered_data = filter_corpus_data(corpus_data, ["Post", "VanKleeck"])

    assert filtered_data == {
        "Corpora_modified": {
            "Post": {"b": {}},
            "VanKleeck": {"c": {}},
        }
    }


def test_filter_corpus_data_returns_original_data_for_all():
    corpus_data = {"Corpora_modified": {"Brent": {"a": {}}}}

    assert filter_corpus_data(corpus_data, None) == corpus_data


def test_require_corpus_data_root_rejects_custom_root_key():
    corpus_data = {"MyCorpus": {"Brent": {"a": {}}}}

    with pytest.raises(ValueError, match=CORPUS_DATA_ROOT_KEY):
        require_corpus_data_root(corpus_data)


def test_filter_corpus_data_rejects_custom_root_key():
    corpus_data = {"MyCorpus": {"Brent": {"a": {}}, "Post": {"b": {}}}}

    with pytest.raises(ValueError, match=CORPUS_DATA_ROOT_KEY):
        filter_corpus_data(corpus_data, ["Post"])


def test_target_corpora_include_bates_and_providence():
    assert "Bates" in TARGET_CORPORA
    assert "Providence" in TARGET_CORPORA
