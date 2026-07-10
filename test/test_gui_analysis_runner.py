import json
from unittest.mock import patch

from src.gui.services import (
    DEFAULT_ICONICITY_CSV,
    DEFAULT_RATED_OUTPUT_DIR,
    DEFAULT_TYPES_OUTPUT_DIR,
    TYPE_COUNT_ONLY_ONCE,
)
from src.gui_analysis_runner import main


def _read_summary(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_main_tokens_writes_summary_json(tmp_path):
    result_path = tmp_path / "tokens_result.json"
    fake_result = {
        "outputs": {"children": {"json": str(tmp_path / "children.json")}},
        "plot_outputs": None,
    }

    with patch(
        "src.gui_analysis_runner.run_tokens_analysis",
        return_value=fake_result,
    ) as mock_run:
        exit_code = main(
            [
                "tokens",
                "--processed-root",
                "Corpora_modified",
                "--output-dir",
                "custom_tokens",
                "--result-file",
                str(result_path),
            ]
        )

    assert exit_code == 0
    mock_run.assert_called_once_with(
        "Corpora_modified",
        selected_corpora=None,
        output_dir="custom_tokens",
        iconicity_csv=DEFAULT_ICONICITY_CSV,
        generate_plots=False,
        plots_dir=None,
        distribution_dir=None,
    )
    assert _read_summary(result_path) == {
        "outputs": fake_result["outputs"],
        "plot_outputs": None,
    }


def test_main_types_passes_plot_options_and_writes_summary_json(tmp_path):
    result_path = tmp_path / "types_result.json"
    fake_result = {
        "outputs": {"adults": {"summary": str(tmp_path / "summary.csv")}},
        "plot_outputs": {
            "plots_dir": str(tmp_path / "plots"),
            "files": {"total": str(tmp_path / "plots" / "total.png")},
        },
    }

    with patch(
        "src.gui_analysis_runner.run_types_analysis",
        return_value=fake_result,
    ) as mock_run:
        exit_code = main(
            [
                "types",
                "--processed-root",
                "Corpora_modified",
                "--corpus",
                "Brent",
                "--category",
                "noun",
                "--generate-plots",
                "--plots-dir",
                str(tmp_path / "plots"),
                "--plot-count-criteria",
                "children",
                "--type-count-mode",
                TYPE_COUNT_ONLY_ONCE,
                "--result-file",
                str(result_path),
            ]
        )

    assert exit_code == 0
    mock_run.assert_called_once_with(
        "Corpora_modified",
        selected_corpora=["Brent"],
        categories=["noun"],
        output_dir=DEFAULT_TYPES_OUTPUT_DIR,
        iconicity_csv=DEFAULT_ICONICITY_CSV,
        generate_plots=True,
        plots_dir=str(tmp_path / "plots"),
        plot_count_criteria=("children",),
        type_count_mode=TYPE_COUNT_ONLY_ONCE,
    )
    assert _read_summary(result_path) == {
        "outputs": fake_result["outputs"],
        "plot_outputs": fake_result["plot_outputs"],
    }


def test_main_rated_uses_default_processed_root_and_writes_summary_json(tmp_path):
    result_path = tmp_path / "rated_result.json"
    fake_result = {
        "outputs": {
            "source_dir": DEFAULT_TYPES_OUTPUT_DIR,
            "output_dir": DEFAULT_RATED_OUTPUT_DIR,
        }
    }

    with patch(
        "src.gui_analysis_runner.run_rated_export",
        return_value=fake_result,
    ) as mock_run:
        exit_code = main(
            [
                "rated",
                "--result-file",
                str(result_path),
            ]
        )

    assert exit_code == 0
    mock_run.assert_called_once_with(
        source_dir=DEFAULT_TYPES_OUTPUT_DIR,
        output_dir=DEFAULT_RATED_OUTPUT_DIR,
        iconicity_csv=DEFAULT_ICONICITY_CSV,
    )
    assert _read_summary(result_path) == {
        "outputs": fake_result["outputs"],
        "plot_outputs": None,
    }
