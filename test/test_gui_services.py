from unittest.mock import patch

from src.gui.services import (
    get_available_categories,
    get_available_corpora,
    load_corpus_data,
    run_tokens_analysis,
    run_types_analysis,
)


def test_get_available_corpora_delegates_to_discovery():
    with patch("src.gui.services.discover_available_corpora") as mock_discover:
        mock_discover.return_value = ["Brent", "Post"]

        result = get_available_corpora("Corpus_modified")

    assert result == ["Brent", "Post"]


def test_load_corpus_data_reads_and_filters_selected_corpora():
    with patch("src.gui.services.Reader.read_directory") as mock_read_directory:
        mock_read_directory.return_value = {
            "Corpus_modified": {
                "Brent": {"a": {}},
                "Post": {"b": {}},
            }
        }

        result = load_corpus_data("Corpus_modified", selected_corpora=["Post"])

    assert result == {"Corpus_modified": {"Post": {"b": {}}}}


def test_get_available_categories_uses_filtered_corpus_data():
    with patch("src.gui.services.load_corpus_data") as mock_load_corpus_data:
        with patch(
            "src.gui.services.collect_grammatical_categories"
        ) as mock_collect_categories:
            mock_load_corpus_data.return_value = {"Corpus_modified": {"Post": {}}}
            mock_collect_categories.return_value = ["noun", "verb"]

            result = get_available_categories(
                "Corpus_modified", selected_corpora=["Post"]
            )

    assert result == ["noun", "verb"]
    mock_load_corpus_data.assert_called_once_with("Corpus_modified", ["Post"])


def test_run_types_analysis_delegates_to_grammatical_pipeline():
    with patch("src.gui.services.load_corpus_data") as mock_load_corpus_data:
        with patch("src.gui.services.run_grammatical_pipeline") as mock_run_pipeline:
            mock_load_corpus_data.return_value = {"Corpus_modified": {"Post": {}}}
            mock_run_pipeline.return_value = {"outputs": {"children": {}}}

            result = run_types_analysis(
                "Corpus_modified",
                selected_corpora=["Post"],
                categories=["noun"],
                output_dir="salida_types",
            )

    assert result == {"outputs": {"children": {}}}
    mock_run_pipeline.assert_called_once_with(
        {"Corpus_modified": {"Post": {}}},
        output_dir="salida_types",
        grammatical_categories=["noun"],
    )


def test_run_tokens_analysis_exports_valid_word_stats():
    with patch("src.gui.services.load_corpus_data") as mock_load_corpus_data:
        with patch("src.gui.services.process_data_with_formatter") as mock_process:
            with patch("src.gui.services.group_data_by_age") as mock_group:
                with patch("src.gui.services.DataFormatter.format_csv_data_from") as mock_csv:
                    with patch("src.gui.services.IconicityModel") as mock_model:
                        with patch(
                            "src.gui.services.create_age_group_statistics"
                        ) as mock_age_stats:
                            with patch(
                                "src.gui.services.process_valid_words_by_age_group"
                            ) as mock_valid_words:
                                with patch(
                                    "src.gui.services.ValidWordsStatsExporter.export"
                                ) as mock_export:
                                    mock_load_corpus_data.return_value = {
                                        "Corpus_modified": {"Post": {}}
                                    }
                                    mock_process.return_value = {"processed": True}
                                    mock_group.return_value = {"01Y01Q": {}}
                                    mock_csv.return_value = {"1": {"word": "wow"}}
                                    mock_model.return_value = object()
                                    mock_age_stats.return_value = {"01Y01Q": {}}
                                    mock_valid_words.return_value = {
                                        "01Y01Q": {"children": {}, "adults": {}}
                                    }
                                    mock_export.return_value = {"children": {}}

                                    result = run_tokens_analysis(
                                        "Corpus_modified",
                                        selected_corpora=["Post"],
                                        output_dir="salida_tokens",
                                        iconicity_csv="iconicity.csv",
                                        generate_plots=False,
                                    )

    assert result["outputs"] == {"children": {}}
    assert result["plot_outputs"] is None
    mock_export.assert_called_once_with(
        {"01Y01Q": {"children": {}, "adults": {}}}
    )
