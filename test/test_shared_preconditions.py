from src.analysis.shared_preconditions import (
    PLOT_MODULES,
    inspect_processed_corpora,
    missing_selected_corpora,
    rated_source_ready,
    required_analysis_modules,
)
from src.gui.app import ChildConicityApp


def test_processed_corpora_require_the_canonical_name_and_a_child(tmp_path):
    wrong_name = tmp_path / "Corpor_modified" / "Brent"
    wrong_name.mkdir(parents=True)
    empty = tmp_path / "Corpora_modified"
    empty.mkdir()

    wrong = inspect_processed_corpora(str(wrong_name.parent))
    assert wrong["name_ok"] is False
    assert wrong["corpora"] == ["Brent"]

    named = inspect_processed_corpora(str(empty))
    assert named["name_ok"] is True
    assert named["ready"] is False

    (empty / "Post").mkdir()
    ready = inspect_processed_corpora(str(empty))
    assert ready["ready"] is True
    assert ready["corpora"] == ["Post"]
    assert missing_selected_corpora(str(empty), ["Brent"], ready["corpora"]) == ["Brent"]


def test_rated_source_ready_requires_word_count_directory(tmp_path):
    source = tmp_path / "quarterly_grammatical_categories"
    source.mkdir()
    assert rated_source_ready(str(source)) is False

    (source / "Brent" / "WordCount").mkdir(parents=True)
    assert rated_source_ready(str(source)) is True


def test_plot_modules_are_required_only_when_generating_plots():
    assert required_analysis_modules("tokens", False) == ["pandas"]
    assert required_analysis_modules("tokens", True) == ["pandas", *PLOT_MODULES]
    assert required_analysis_modules("types", False) == []
    assert required_analysis_modules("types", True) == ["pandas", *PLOT_MODULES]
    assert required_analysis_modules("rated", True) == []


def test_gui_analysis_validation_uses_the_shared_processed_check(tmp_path):
    processed = tmp_path / "Corpora_modified"
    processed.mkdir()
    app = object.__new__(ChildConicityApp)

    error = app._validate_analysis_inputs(str(processed), None)

    assert str(processed) in error
