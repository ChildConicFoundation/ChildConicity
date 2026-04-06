from src.analysis.age_group_analysis import (
    create_age_group_statistics,
    process_valid_words_by_age_group,
)
from src.analysis.iconicity_model import IconicityModel
from src.data_io.corpus_processing import process_data_with_formatter
from src.data_io.corpus_selection import (
    discover_available_corpora,
    filter_corpus_data,
)
from src.data_io.data_formatter import DataFormatter
from src.data_io.grammatical_corpus_processing import (
    collect_grammatical_categories,
    run_grammatical_pipeline,
)
from src.data_io.reader import Reader
from src.quarterly_samples import ValidWordsStatsExporter, group_data_by_age


DEFAULT_TOKENS_OUTPUT_DIR = "quarterly_valid_words"
DEFAULT_TYPES_OUTPUT_DIR = "quarterly_grammatical_categories"
DEFAULT_ICONICITY_CSV = "iconicity_ratings_cleaned.csv"
DEFAULT_PLOTS_DIR = "iconic_vs_noniconic"
DEFAULT_DISTRIBUTION_DIR = "pruebas"


def load_corpus_data(processed_root, selected_corpora=None):
    reader = Reader()
    corpus_data = reader.read_directory(processed_root)
    return filter_corpus_data(corpus_data, selected_corpora)


def get_available_corpora(processed_root):
    return discover_available_corpora(processed_root)


def get_available_categories(processed_root, selected_corpora=None):
    corpus_data = load_corpus_data(processed_root, selected_corpora)
    return collect_grammatical_categories(corpus_data)


def run_types_analysis(
    processed_root,
    selected_corpora=None,
    categories=None,
    output_dir=DEFAULT_TYPES_OUTPUT_DIR,
):
    corpus_data = load_corpus_data(processed_root, selected_corpora)
    return run_grammatical_pipeline(
        corpus_data,
        output_dir=output_dir,
        grammatical_categories=categories,
    )


def run_tokens_analysis(
    processed_root,
    selected_corpora=None,
    output_dir=DEFAULT_TOKENS_OUTPUT_DIR,
    iconicity_csv=DEFAULT_ICONICITY_CSV,
    generate_plots=False,
    plots_dir=DEFAULT_PLOTS_DIR,
    distribution_dir=DEFAULT_DISTRIBUTION_DIR,
):
    corpus_data = load_corpus_data(processed_root, selected_corpora)
    processed_data = process_data_with_formatter(corpus_data)
    grouped_data = group_data_by_age(processed_data)

    formatter = DataFormatter()
    csv_data = formatter.format_csv_data_from(iconicity_csv)
    iconicity_model = IconicityModel(csv_data)

    age_group_stats = create_age_group_statistics(grouped_data, iconicity_model)
    valid_words_stats = process_valid_words_by_age_group(
        age_group_stats, iconicity_model
    )
    outputs = ValidWordsStatsExporter(output_dir).export(valid_words_stats)

    plot_outputs = None
    if generate_plots:
        plot_outputs = _generate_token_plots(
            valid_words_stats,
            plots_dir=plots_dir,
            distribution_dir=distribution_dir,
        )

    return {
        "processed_data": processed_data,
        "grouped_data": grouped_data,
        "age_group_stats": age_group_stats,
        "valid_words_stats": valid_words_stats,
        "outputs": outputs,
        "plot_outputs": plot_outputs,
    }


def _generate_token_plots(valid_words_stats, plots_dir, distribution_dir):
    import os

    from src.visualization.data_analysis_plotter import DataAnalysisPlotter

    plotter = DataAnalysisPlotter(valid_words_stats)
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(distribution_dir, exist_ok=True)

    by_age_path = os.path.join(plots_dir, "iconic_vs_non_iconic_by_age.png")
    adults_path = os.path.join(plots_dir, "iconic_vs_non_iconic_by_age_adults.png")
    children_path = os.path.join(plots_dir, "iconic_vs_non_iconic_by_age_children.png")
    all_adults_path = os.path.join(
        distribution_dir, "distribucion_iconicidad_todos_adultos.png"
    )
    all_children_path = os.path.join(
        distribution_dir, "distribucion_iconicidad_todos_ninos.png"
    )

    plotter.plot_iconic_vs_non_iconic_by_age(by_age_path)
    plotter.plot_iconic_vs_non_iconic_by_age_adults(adults_path)
    plotter.plot_iconic_vs_non_iconic_by_age_children(children_path)
    plotter.plot_iconicity_distribution_by_age_group(save_dir=distribution_dir)
    plotter.plot_all_adults_iconicity_distribution(all_adults_path)
    plotter.plot_all_children_iconicity_distribution(all_children_path)

    return {
        "plots_dir": plots_dir,
        "distribution_dir": distribution_dir,
        "files": {
            "by_age": by_age_path,
            "adults": adults_path,
            "children": children_path,
            "all_adults_distribution": all_adults_path,
            "all_children_distribution": all_children_path,
        },
    }
