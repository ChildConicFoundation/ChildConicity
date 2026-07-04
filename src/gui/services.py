import os

from src.analysis.age_group_analysis import (
    create_age_group_statistics,
    process_valid_words_by_age_group,
)
from src.analysis.grammatical_type_analysis import (
    DEFAULT_TYPE_COUNT_MODE,
    TYPE_COUNT_ONLY_ONCE,
    TYPE_COUNT_WITH_REPETITIONS,
    create_grammatical_type_stats,
    create_grammatical_type_stats_by_category,
    normalize_type_count_mode,
)
from src.analysis.iconicity_model import IconicityModel
from src.data_io.corpus_processing import process_data_with_formatter
from src.data_io.corpus_selection import (
    CORPUS_DATA_ROOT_KEY,
    discover_available_corpora,
    filter_corpus_data,
    require_corpus_data_root_path,
)
from src.data_io.data_formatter import DataFormatter
from src.data_io.grammatical_corpus_processing import (
    process_grammatical_data_with_formatter,
    run_grammatical_pipeline,
)
from src.data_io.reader import Reader
from src.quarterly_samples import ValidWordsStatsExporter, group_data_by_age
from src.quarterly_samples.rated_exporter import export_rated


DEFAULT_TOKENS_OUTPUT_DIR = "quarterly_valid_words"
DEFAULT_TYPES_OUTPUT_DIR = "quarterly_grammatical_categories"
DEFAULT_RATED_OUTPUT_DIR = "rated_quarterly_grammatical_categories"
DEFAULT_ICONICITY_CSV = "iconicity_ratings/iconicity_ratings_cleaned.csv"
DEFAULT_PLOTS_DIR = "iconic_vs_noniconic"
DEFAULT_DISTRIBUTION_DIR = "distribution"
DEFAULT_PLOT_COUNT_CRITERIA = ("adults", "children")
DEFAULT_GRAMMATICAL_CATEGORIES = (
    "noun",
    "verb",
    "adj",
    "adv",
    "pron",
    "det",
    "propn",
    "num",
    "adp",
    "aux",
    "part",
    "cconj",
    "sconj",
    "intj",
    "punct",
    "ls",
    "L2",
    "b",
    "c",
    "cm",
    "d",
    "f",
    "g",
    "i",
    "k",
    "l",
    "n",
    "o",
    "p",
    "q",
    "si",
    "t",
    "u",
    "wp",
    "x",
)


def load_corpus_data(processed_root, selected_corpora=None):
    reader = Reader()
    require_corpus_data_root_path(processed_root)
    if selected_corpora is None:
        corpus_data = reader.read_directory(processed_root)
        return filter_corpus_data(corpus_data, selected_corpora)

    filtered_root = {}
    for corpus_name in selected_corpora:
        corpus_path = os.path.join(processed_root, corpus_name)
        try:
            corpus_data = reader.read_directory(corpus_path)
        except FileNotFoundError:
            continue

        if corpus_name in corpus_data:
            filtered_root[corpus_name] = corpus_data[corpus_name]

    return {CORPUS_DATA_ROOT_KEY: filtered_root}


def get_available_corpora(processed_root):
    return discover_available_corpora(processed_root)


def get_available_categories(processed_root, selected_corpora=None):
    return list(DEFAULT_GRAMMATICAL_CATEGORIES)


def run_types_analysis(
    processed_root,
    selected_corpora=None,
    categories=None,
    output_dir=DEFAULT_TYPES_OUTPUT_DIR,
    iconicity_csv=DEFAULT_ICONICITY_CSV,
    generate_plots=False,
    plots_dir=None,
    plot_count_criteria=DEFAULT_PLOT_COUNT_CRITERIA,
    type_count_mode=DEFAULT_TYPE_COUNT_MODE,
):
    corpora_to_load = selected_corpora or get_available_corpora(processed_root)
    print(f"Loading processed corpus from {processed_root}...")
    print(
        "Corpora to load "
        f"({len(corpora_to_load)}): {', '.join(corpora_to_load) if corpora_to_load else '(none)'}"
    )
    corpus_data = load_corpus_data(processed_root, selected_corpora)
    print("Corpora loaded.")
    if generate_plots:
        print("Exporting standard grammatical data for types...")
    else:
        print("Processing grammatical data and exporting results...")
    result = run_grammatical_pipeline(
        corpus_data,
        output_dir=output_dir,
        grammatical_categories=categories,
    )
    if generate_plots:
        print(
            "Standard grammatical export completed. "
            "The selected count mode only affects plots."
        )
    else:
        print("Grammatical export completed.")

    if not generate_plots:
        return result

    print("Loading iconicity ratings...")
    formatter = DataFormatter()
    csv_data = formatter.format_csv_data_from(iconicity_csv)
    iconicity_model = IconicityModel(csv_data)

    grouped_data_for_plots = result["grouped_data"]
    if categories is not None:
        print(
            "Reprocessing unfiltered data to preserve global plot totals..."
        )
        processed_data_for_plots = process_grammatical_data_with_formatter(corpus_data)
        grouped_data_for_plots = group_data_by_age(processed_data_for_plots)

    result = result.copy()
    selected_type_count_mode = normalize_type_count_mode(type_count_mode)
    print(
        "Generating type plots "
        f"con criterio de conteo: {_type_count_mode_label(selected_type_count_mode)}..."
    )
    result["plot_outputs"] = _generate_type_plots(
        grouped_data_for_plots,
        iconicity_model,
        categories_to_plot=categories,
        plot_count_criteria=plot_count_criteria,
        type_count_mode=selected_type_count_mode,
        plots_dir=plots_dir
        or _default_types_plots_dir(
            output_dir,
            categories,
            type_count_mode=selected_type_count_mode,
        ),
    )
    return result


def run_tokens_analysis(
    processed_root,
    selected_corpora=None,
    output_dir=DEFAULT_TOKENS_OUTPUT_DIR,
    iconicity_csv=DEFAULT_ICONICITY_CSV,
    generate_plots=False,
    plots_dir=DEFAULT_PLOTS_DIR,
    distribution_dir=DEFAULT_DISTRIBUTION_DIR,
):
    corpora_to_load = selected_corpora or get_available_corpora(processed_root)
    print(f"Loading processed corpus from {processed_root}...")
    print(
        "Corpora to load "
        f"({len(corpora_to_load)}): {', '.join(corpora_to_load) if corpora_to_load else '(none)'}"
    )
    corpus_data = load_corpus_data(processed_root, selected_corpora)
    print("Corpora loaded.")
    print("Processing corpus by tokens...")
    processed_data = process_data_with_formatter(corpus_data)
    grouped_data = group_data_by_age(processed_data)

    print("Loading iconicity ratings...")
    formatter = DataFormatter()
    csv_data = formatter.format_csv_data_from(iconicity_csv)
    iconicity_model = IconicityModel(csv_data)

    print("Computing statistics by age group...")
    age_group_stats = create_age_group_statistics(grouped_data, iconicity_model)
    valid_words_stats = process_valid_words_by_age_group(
        age_group_stats, iconicity_model
    )
    print("Exporting valid word statistics...")
    outputs = ValidWordsStatsExporter(output_dir).export(valid_words_stats)

    plot_outputs = None
    if generate_plots:
        print("Generating token plots...")
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
        distribution_dir, "iconicity_distribution_all_adults.png"
    )
    all_children_path = os.path.join(
        distribution_dir, "iconicity_distribution_all_children.png"
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


def _generate_type_plots(
    grouped_data,
    iconicity_model,
    plots_dir,
    categories_to_plot=None,
    plot_count_criteria=DEFAULT_PLOT_COUNT_CRITERIA,
    type_count_mode=DEFAULT_TYPE_COUNT_MODE,
):
    import os

    from src.visualization.data_analysis_plotter import DataAnalysisPlotter

    selected_type_count_mode = normalize_type_count_mode(type_count_mode)
    os.makedirs(plots_dir, exist_ok=True)

    print("Preparing global statistics for plots...")
    total_stats = create_grammatical_type_stats(
        grouped_data,
        iconicity_model,
        count_mode=selected_type_count_mode,
    )
    stats_by_scope = {"total": total_stats}
    print("Preparing statistics by category...")
    category_stats = create_grammatical_type_stats_by_category(
        grouped_data,
        iconicity_model,
        count_mode=selected_type_count_mode,
    )
    selected_category_stats = _select_type_plot_categories(
        category_stats,
        categories_to_plot,
    )
    stats_by_scope.update(selected_category_stats)
    print(
        "Categories included in plots: "
        f"{len(selected_category_stats)}"
    )
    print(
        "Rendering images by age group: "
        f"{len(total_stats)}"
    )

    files = DataAnalysisPlotter(total_stats).plot_iconicity_distribution_scopes_by_age_group(
        stats_by_scope,
        save_dir=plots_dir,
        filename_prefix="iconicity_distribution_types",
        title_suffix=f" - Types ({_type_count_mode_label(selected_type_count_mode)})",
        speaker_groups_to_plot=plot_count_criteria,
        print_progress=True,
        print_warnings=False,
    )

    return {
        "plots_dir": plots_dir,
        "files": files,
    }


def _select_type_plot_categories(category_stats, categories_to_plot):
    if categories_to_plot is None:
        return category_stats

    selected_categories = {
        category.casefold()
        for category in categories_to_plot
    }
    return {
        category: stats
        for category, stats in category_stats.items()
        if category.casefold() in selected_categories
    }


def _default_types_plots_dir(
    output_dir,
    categories_to_plot=None,
    type_count_mode=DEFAULT_TYPE_COUNT_MODE,
):
    import os

    return os.path.join(
        output_dir or DEFAULT_TYPES_OUTPUT_DIR,
        _types_plots_dir_name(
            categories_to_plot,
            type_count_mode=type_count_mode,
        ),
    )


def _types_plots_dir_name(
    categories_to_plot=None,
    type_count_mode=DEFAULT_TYPE_COUNT_MODE,
):
    if categories_to_plot is None:
        base_name = "plots_count_criteria_all"
    else:
        categories = [
            _safe_plot_dir_part(category)
            for category in categories_to_plot
            if _safe_plot_dir_part(category)
        ]
        if not categories:
            base_name = "plots_count_criteria_all"
        else:
            base_name = "plots_count_criteria_" + "_".join(categories)

    if normalize_type_count_mode(type_count_mode) == TYPE_COUNT_ONLY_ONCE:
        return f"{base_name}_only_once"

    return base_name


def run_rated_export(
    source_dir=DEFAULT_TYPES_OUTPUT_DIR,
    output_dir=DEFAULT_RATED_OUTPUT_DIR,
    iconicity_csv=DEFAULT_ICONICITY_CSV,
):
    print(f"Enriching WordCount from {source_dir}...")
    export_rated(
        source_root=source_dir,
        output_root=output_dir,
        iconicity_csv=iconicity_csv,
    )
    print("Rated export completed.")
    return {
        "outputs": {
            "source_dir": source_dir,
            "output_dir": output_dir,
        }
    }


def _type_count_mode_label(type_count_mode):
    if type_count_mode == TYPE_COUNT_ONLY_ONCE:
        return "Only once"

    if type_count_mode == TYPE_COUNT_WITH_REPETITIONS:
        return "With repetitions"

    return "With repetitions"


def _safe_plot_dir_part(value):
    safe_chars = []
    for char in str(value).casefold():
        if char.isalnum():
            safe_chars.append(char)
        else:
            safe_chars.append("_")

    return "_".join("".join(safe_chars).split("_"))
