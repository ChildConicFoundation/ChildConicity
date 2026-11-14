from unittest.mock import patch

import pytest

from src.gui.services import (
    DEFAULT_GRAMMATICAL_CATEGORIES,
    TYPE_COUNT_ONLY_ONCE,
    TYPE_COUNT_WITH_REPETITIONS,
    _generate_token_plots,
    _generate_type_plots,
    _safe_plot_dir_part,
    _select_type_plot_categories,
    _type_count_mode_label,
    _types_plots_dir_name,
    get_available_categories,
    get_available_corpora,
    load_corpus_data,
    run_rated_export,
    run_tokens_analysis,
    run_types_analysis,
)


def test_load_corpus_data_rejects_custom_processed_root():
    with patch("src.gui.services.Reader.read_directory") as mock_read_directory:
        mock_read_directory.return_value = {
            "CustomRoot": {"Post": {"b": {}}}
        }

        with pytest.raises(ValueError, match="Corpora_modified"):
            load_corpus_data("/data/CustomRoot")

    mock_read_directory.assert_not_called()


def test_load_corpus_data_rejects_custom_processed_root_with_selected_corpora():
    with patch("src.gui.services.Reader.read_directory") as mock_read_directory:
        with pytest.raises(ValueError, match="Corpora_modified"):
            load_corpus_data("/data/CustomRoot", selected_corpora=["Post"])

    mock_read_directory.assert_not_called()


def test_get_available_corpora_delegates_to_discovery():
    with patch("src.gui.services.discover_available_corpora") as mock_discover:
        mock_discover.return_value = ["Brent", "Post"]

        result = get_available_corpora("Corpora_modified")

    assert result == ["Brent", "Post"]


def test_load_corpus_data_reads_the_whole_root_when_no_corpus_is_selected():
    with patch("src.gui.services.Reader.read_directory") as mock_read_directory:
        mock_read_directory.return_value = {
            "Corpora_modified": {"Post": {"child": {}}}
        }

        result = load_corpus_data("Corpora_modified")

    assert result == {"Corpora_modified": {"Post": {"child": {}}}}
    mock_read_directory.assert_called_once_with("Corpora_modified")


def test_load_corpus_data_reads_and_filters_selected_corpora():
    with patch("src.gui.services.Reader.read_directory") as mock_read_directory:
        mock_read_directory.return_value = {"Post": {"b": {}}}

        result = load_corpus_data("Corpora_modified", selected_corpora=["Post"])

    assert result == {"Corpora_modified": {"Post": {"b": {}}}}
    mock_read_directory.assert_called_once_with("Corpora_modified/Post")


def test_load_corpus_data_skips_missing_selected_corpora():
    with patch("src.gui.services.Reader.read_directory") as mock_read_directory:
        mock_read_directory.side_effect = FileNotFoundError

        result = load_corpus_data("Corpora_modified", selected_corpora=["Missing"])

    assert result == {"Corpora_modified": {}}
    mock_read_directory.assert_called_once_with("Corpora_modified/Missing")


def test_get_available_categories_returns_static_categories():
    result = get_available_categories(
        "Corpora_modified", selected_corpora=["Post"]
    )

    assert result == list(DEFAULT_GRAMMATICAL_CATEGORIES)


def test_run_types_analysis_delegates_to_grammatical_pipeline():
    with patch("src.gui.services.load_corpus_data") as mock_load_corpus_data:
        with patch("src.gui.services.run_grammatical_pipeline") as mock_run_pipeline:
            mock_load_corpus_data.return_value = {"Corpora_modified": {"Post": {}}}
            mock_run_pipeline.return_value = {"outputs": {"children": {}}}

            result = run_types_analysis(
                "Corpora_modified",
                selected_corpora=["Post"],
                categories=["noun"],
                output_dir="output_types",
            )

    assert result == {"outputs": {"children": {}}}
    mock_run_pipeline.assert_called_once_with(
        {"Corpora_modified": {"Post": {}}},
        output_dir="output_types",
        grammatical_categories=["noun"],
    )


def test_run_types_analysis_can_generate_type_plots():
    with patch("src.gui.services.load_corpus_data") as mock_load_corpus_data:
        with patch("src.gui.services.run_grammatical_pipeline") as mock_run_pipeline:
            with patch("src.gui.services.DataFormatter.format_csv_data_from") as mock_csv:
                with patch("src.gui.services.IconicityModel") as mock_model:
                    with patch("src.gui.services._generate_type_plots") as mock_plots:
                        mock_load_corpus_data.return_value = {
                            "Corpora_modified": {"Post": {}}
                        }
                        mock_run_pipeline.return_value = {
                            "grouped_data": {"01Y01Q": {}},
                            "outputs": {"children": {}},
                        }
                        mock_csv.return_value = {"1": {"word": "ball"}}
                        mock_model.return_value = object()
                        mock_plots.return_value = {"plots_dir": "plots_types"}

                        result = run_types_analysis(
                            "Corpora_modified",
                            output_dir="output_types",
                            iconicity_csv="iconicity.csv",
                            generate_plots=True,
                            plots_dir="plots_types",
                        )

    assert result["plot_outputs"] == {"plots_dir": "plots_types"}
    mock_csv.assert_called_once_with("iconicity.csv")
    mock_plots.assert_called_once_with(
        {"01Y01Q": {}},
        mock_model.return_value,
        categories_to_plot=None,
        plot_count_criteria=("adults", "children"),
        type_count_mode="with_repetitions",
        plots_dir="plots_types",
    )


def test_run_types_analysis_uses_category_named_plots_dir_by_default():
    with patch("src.gui.services.load_corpus_data") as mock_load_corpus_data:
        with patch("src.gui.services.run_grammatical_pipeline") as mock_run_pipeline:
            with patch(
                "src.gui.services.process_grammatical_data_with_formatter"
            ) as mock_process_all_categories:
                with patch("src.gui.services.group_data_by_age") as mock_group:
                    with patch("src.gui.services.DataFormatter.format_csv_data_from"):
                        with patch("src.gui.services.IconicityModel") as mock_model:
                            with patch("src.gui.services._generate_type_plots") as mock_plots:
                                corpus_data = {"Corpora_modified": {"Post": {}}}
                                mock_load_corpus_data.return_value = corpus_data
                                mock_run_pipeline.return_value = {
                                    "grouped_data": {"filtered": True},
                                    "outputs": {"children": {}},
                                }
                                mock_process_all_categories.return_value = {
                                    "processed": "all_categories"
                                }
                                mock_group.return_value = {"all_categories": True}
                                mock_model.return_value = object()
                                mock_plots.return_value = {"plots_dir": "ignored"}

                                run_types_analysis(
                                    "Corpora_modified",
                                    categories=["adj", "noun"],
                                    output_dir="output_types",
                                    generate_plots=True,
                                )

    mock_process_all_categories.assert_called_once_with(corpus_data)
    mock_group.assert_called_once_with({"processed": "all_categories"})
    mock_plots.assert_called_once_with(
        {"all_categories": True},
        mock_model.return_value,
        categories_to_plot=["adj", "noun"],
        plot_count_criteria=("adults", "children"),
        type_count_mode="with_repetitions",
        plots_dir="output_types/plots_count_criteria_adj_noun",
    )


def test_run_types_analysis_uses_only_once_plots_dir_suffix_by_default():
    with patch("src.gui.services.load_corpus_data") as mock_load_corpus_data:
        with patch("src.gui.services.run_grammatical_pipeline") as mock_run_pipeline:
            with patch("src.gui.services.DataFormatter.format_csv_data_from"):
                with patch("src.gui.services.IconicityModel") as mock_model:
                    with patch("src.gui.services._generate_type_plots") as mock_plots:
                        mock_load_corpus_data.return_value = {
                            "Corpora_modified": {"Post": {}}
                        }
                        mock_run_pipeline.return_value = {
                            "grouped_data": {"01Y01Q": {}},
                            "outputs": {"children": {}},
                        }
                        mock_model.return_value = object()
                        mock_plots.return_value = {"plots_dir": "ignored"}

                        run_types_analysis(
                            "Corpora_modified",
                            output_dir="output_types",
                            generate_plots=True,
                            type_count_mode=TYPE_COUNT_ONLY_ONCE,
                        )

    mock_plots.assert_called_once_with(
        {"01Y01Q": {}},
        mock_model.return_value,
        categories_to_plot=None,
        plot_count_criteria=("adults", "children"),
        type_count_mode=TYPE_COUNT_ONLY_ONCE,
        plots_dir="output_types/plots_count_criteria_all_only_once",
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
                                        "Corpora_modified": {"Post": {}}
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
                                        "Corpora_modified",
                                        selected_corpora=["Post"],
                                        output_dir="output_tokens",
                                        iconicity_csv="iconicity.csv",
                                        generate_plots=False,
                                    )

    assert result["outputs"] == {"children": {}}
    assert result["plot_outputs"] is None
    mock_export.assert_called_once_with(
        {"01Y01Q": {"children": {}, "adults": {}}}
    )


def test_run_tokens_analysis_can_generate_token_plots():
    with patch("src.gui.services.load_corpus_data") as mock_load_corpus_data:
        with patch("src.gui.services.process_data_with_formatter"):
            with patch("src.gui.services.group_data_by_age"):
                with patch("src.gui.services.DataFormatter.format_csv_data_from"):
                    with patch("src.gui.services.IconicityModel"):
                        with patch("src.gui.services.create_age_group_statistics"):
                            with patch("src.gui.services.process_valid_words_by_age_group") as mock_valid_words:
                                with patch("src.gui.services.ValidWordsStatsExporter.export"):
                                    with patch("src.gui.services._generate_token_plots") as mock_plots:
                                        mock_load_corpus_data.return_value = {
                                            "Corpora_modified": {"Post": {}}
                                        }
                                        mock_valid_words.return_value = {"01Y01Q": {}}
                                        mock_plots.return_value = {"plots_dir": "token-plots"}

                                        result = run_tokens_analysis(
                                            "Corpora_modified",
                                            selected_corpora=["Post"],
                                            generate_plots=True,
                                            plots_dir="token-plots",
                                            distribution_dir="token-dist",
                                        )

    assert result["plot_outputs"] == {"plots_dir": "token-plots"}
    mock_plots.assert_called_once_with(
        {"01Y01Q": {}},
        plots_dir="token-plots",
        distribution_dir="token-dist",
    )


def test_generate_token_plots_asks_the_plotter_for_each_figure(tmp_path):
    with patch(
        "src.visualization.data_analysis_plotter.DataAnalysisPlotter"
    ) as plotter_cls:
        result = _generate_token_plots(
            {"01Y01Q": {}},
            plots_dir=str(tmp_path / "plots"),
            distribution_dir=str(tmp_path / "distribution"),
        )

    plotter = plotter_cls.return_value
    plotter.plot_iconic_vs_non_iconic_by_age.assert_called_once()
    plotter.plot_iconic_vs_non_iconic_by_age_adults.assert_called_once()
    plotter.plot_iconic_vs_non_iconic_by_age_children.assert_called_once()
    plotter.plot_iconicity_distribution_by_age_group.assert_called_once()
    plotter.plot_all_adults_iconicity_distribution.assert_called_once()
    plotter.plot_all_children_iconicity_distribution.assert_called_once()
    assert result["plots_dir"].endswith("plots")
    assert set(result["files"]) == {
        "by_age",
        "adults",
        "children",
        "all_adults_distribution",
        "all_children_distribution",
    }


def test_generate_type_plots_keeps_only_the_requested_categories(tmp_path):
    with patch(
        "src.gui.services.create_grammatical_type_stats",
        return_value={"01Y01Q": {}},
    ):
        with patch(
            "src.gui.services.create_grammatical_type_stats_by_category",
            return_value={"noun": {"01Y01Q": {}}, "verb": {"01Y01Q": {}}},
        ):
            with patch(
                "src.visualization.data_analysis_plotter.DataAnalysisPlotter"
            ) as plotter_cls:
                plotter_cls.return_value.plot_iconicity_distribution_scopes_by_age_group.return_value = [
                    "noun.png"
                ]

                result = _generate_type_plots(
                    {"01Y01Q": {}},
                    object(),
                    plots_dir=str(tmp_path / "plots"),
                    categories_to_plot=["Noun"],
                )

    stats_by_scope = plotter_cls.return_value.plot_iconicity_distribution_scopes_by_age_group.call_args.args[0]
    assert set(stats_by_scope) == {"total", "noun"}
    assert result["files"] == ["noun.png"]


def test_plot_directory_names_drop_empty_and_unknown_count_modes():
    assert _select_type_plot_categories({"noun": 1}, None) == {"noun": 1}
    assert _select_type_plot_categories({"noun": 1, "verb": 2}, ["VERB"]) == {"verb": 2}
    assert _types_plots_dir_name([""]) == "plots_count_criteria_all"
    assert _types_plots_dir_name(["noun-verb"]) == "plots_count_criteria_noun_verb"
    assert _safe_plot_dir_part("noun-verb") == "noun_verb"
    assert _type_count_mode_label(TYPE_COUNT_ONLY_ONCE) == "Only once"
    assert _type_count_mode_label(TYPE_COUNT_WITH_REPETITIONS) == "With repetitions"
    assert _type_count_mode_label("other") == "With repetitions"


def test_run_rated_export_returns_the_source_and_output(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "src.gui.services.export_rated",
        lambda **kwargs: calls.append(kwargs),
    )

    result = run_rated_export(
        source_dir="quarterly",
        output_dir="rated",
        iconicity_csv="ratings.csv",
    )

    assert calls == [
        {
            "source_root": "quarterly",
            "output_root": "rated",
            "iconicity_csv": "ratings.csv",
        }
    ]
    assert result["outputs"] == {"source_dir": "quarterly", "output_dir": "rated"}
