from src.gui.app import _token_plot_directories


def test_token_plot_directories_are_derived_from_output_dir():
    plots_dir, distribution_dir = _token_plot_directories("output_tokens")

    assert plots_dir == "output_tokens/iconic_vs_noniconic"
    assert distribution_dir == "output_tokens/distribution"


def test_token_plot_directories_fall_back_to_default_output_dir():
    plots_dir, distribution_dir = _token_plot_directories("")

    assert plots_dir == "quarterly_valid_words/iconic_vs_noniconic"
    assert distribution_dir == "quarterly_valid_words/distribution"
