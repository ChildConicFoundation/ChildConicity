from src.gui.app import ChildConicityApp, _token_plot_directories


def test_token_plot_directories_are_derived_from_output_dir():
    plots_dir, distribution_dir = _token_plot_directories("output_tokens")

    assert plots_dir == "output_tokens/iconic_vs_noniconic"
    assert distribution_dir == "output_tokens/distribution"


def test_token_plot_directories_fall_back_to_default_output_dir():
    plots_dir, distribution_dir = _token_plot_directories("")

    assert plots_dir == "quarterly_valid_words/iconic_vs_noniconic"
    assert distribution_dir == "quarterly_valid_words/distribution"


def test_initialize_validation_rejects_misspelled_processed_root(tmp_path):
    source_root = tmp_path / "Corpora"
    source_root.mkdir()
    app = object.__new__(ChildConicityApp)

    error = app._validate_initialize_inputs(
        str(source_root),
        str(tmp_path / "Corpor_modified"),
    )

    assert "Corpora_modified" in error


def test_initialize_validation_rejects_missing_source_root(tmp_path):
    app = object.__new__(ChildConicityApp)

    error = app._validate_initialize_inputs(
        str(tmp_path / "Missing"),
        str(tmp_path / "Corpora_modified"),
    )

    assert str(tmp_path / "Missing") in error
