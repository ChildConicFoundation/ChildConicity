import importlib.util

from src.analysis.shared_preconditions import PLOT_MODULES
from src.mcp_server.mcp_preconditions import check_preconditions


def test_check_preconditions_reports_missing_inputs(tmp_path):
    report = check_preconditions(tmp_path)

    assert report["project_root"] == str(tmp_path.resolve())
    assert report["checks"]["iconicity_ratings"]["ok"] is False
    assert report["checks"]["processed_corpora"]["ok"] is False
    assert report["checks"]["processed_corpora"]["corpora"] == []
    assert report["checks"]["grammatical_categories"]["ok"] is False
    assert report["ready_for"]["tokens"] is False
    assert report["ready_for"]["types"] is False
    assert report["ready_for"]["rated"] is False


def test_check_preconditions_ready_for_tokens_types_and_rated(tmp_path):
    ratings = tmp_path / "iconicity_ratings"
    ratings.mkdir()
    (ratings / "iconicity_ratings_cleaned.csv").write_text("word,rating\n", encoding="utf-8")
    processed = tmp_path / "Corpora_modified" / "Brent"
    processed.mkdir(parents=True)
    (
        tmp_path / "quarterly_grammatical_categories" / "Brent" / "WordCount"
    ).mkdir(parents=True)

    report = check_preconditions(tmp_path)

    assert report["checks"]["iconicity_ratings"]["ok"] is True
    assert report["checks"]["processed_corpora"]["corpora"] == ["Brent"]
    assert report["checks"]["grammatical_categories"]["ok"] is True
    assert report["ready_for"]["tokens"] is True
    assert report["ready_for"]["types"] is True
    assert report["ready_for"]["rated"] is True


def test_grammatical_directory_without_word_counts_is_not_ready(tmp_path):
    ratings = tmp_path / "iconicity_ratings"
    ratings.mkdir()
    (ratings / "iconicity_ratings_cleaned.csv").write_text("word,rating\n", encoding="utf-8")
    (tmp_path / "quarterly_grammatical_categories").mkdir()

    report = check_preconditions(tmp_path)

    assert report["checks"]["grammatical_categories"]["ok"] is False
    assert report["ready_for"]["rated"] is False


def test_empty_processed_directory_is_not_ready(tmp_path):
    ratings = tmp_path / "iconicity_ratings"
    ratings.mkdir()
    (ratings / "iconicity_ratings_cleaned.csv").write_text("word,rating\n", encoding="utf-8")
    (tmp_path / "Corpora_modified").mkdir()

    report = check_preconditions(tmp_path)

    assert report["checks"]["processed_corpora"]["ok"] is False
    assert report["ready_for"]["tokens"] is False
    assert report["ready_for"]["rated"] is False


def test_missing_plot_dependency_is_reported(tmp_path, monkeypatch):
    original_find_spec = importlib.util.find_spec

    def find_spec(name):
        if name == "seaborn":
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", find_spec)

    report = check_preconditions(tmp_path)

    assert report["checks"]["plot_dependencies"]["ok"] is False
    assert report["checks"]["plot_dependencies"]["missing"] == ["seaborn"]
    assert report["ready_for"]["plots"] is False
    assert "seaborn" in PLOT_MODULES


def test_present_plot_dependencies_are_ready(tmp_path, monkeypatch):
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())

    report = check_preconditions(tmp_path)

    assert report["checks"]["plot_dependencies"]["missing"] == []
    assert report["ready_for"]["plots"] is True
