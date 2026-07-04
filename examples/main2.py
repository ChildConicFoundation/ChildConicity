import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.initialize_corpuses import main as initialize_corpuses
from src.cli import (
    CorpusCLIOptions,
    add_corpus_options,
    prepare_corpus_cli_options,
)
from src.analysis.age_group_analysis import (
    create_age_group_statistics,
    print_valid_words_statistics,
    process_valid_words_by_age_group,
)
from src.data_io.data_formatter import DataFormatter
from src.analysis.iconicity_model import IconicityModel
from src.data_io.corpus_inspector import print_directory_structure, print_sampled_metadata
from src.data_io.corpus_processing import process_data_with_formatter
from src.data_io.reader import Reader
from src.data_io.corpus_selection import (
    discover_available_corpora,
    filter_corpus_data,
)
from src.quarterly_samples import (
    ValidWordsStatsExporter,
    group_data_by_age,
)
from src.visualization.data_analysis_plotter import DataAnalysisPlotter

def main(argv=None):
    """Main program function"""
    parser = add_corpus_options(
        argparse.ArgumentParser(
            description=(
                "Process the corpus by tokens and filter which corpora to use."
            )
        )
    )
    namespace = parser.parse_args(argv)
    corpus_options = CorpusCLIOptions.from_namespace(namespace)

    source_root = "Corpora"
    output_root = "Corpora_modified"

    # Initialize corpora
    print("Initializing corpora...")
    initialize_corpuses(source_root=source_root, output_root=output_root)
    print("Corpora initialized successfully.")

    available_corpora = discover_available_corpora(output_root)
    corpus_options, should_exit = prepare_corpus_cli_options(
        corpus_options, available_corpora
    )
    if should_exit:
        return 0
    
    # Define input and output directories
    input_dir = output_root
    
    # Create a Reader instance
    reader = Reader()
    
    # Read all directories inside the processed directory
    corpus_data = reader.read_directory(input_dir)
    corpus_data = filter_corpus_data(corpus_data, corpus_options.corpora)
    
    # Show the nested dictionary structure
    print("\nCorpus structure:")
    print_directory_structure(corpus_data)
    
    # Show the first 4 metadata entries for each file
    print("\nFirst 4 metadata entries per file:")
    print_sampled_metadata(corpus_data)
    
    # Process the data using DataFormatter
    print("\nProcessing data with DataFormatter...")
    processed_data = process_data_with_formatter(corpus_data)
    
    # Group data by age
    print("\nGrouping data by age...")
    data_grouped_by_age = group_data_by_age(processed_data)

    # Create the iconicity model
    print("\nCreating iconicity model...")
    formatter = DataFormatter()
    csv_data = formatter.format_csv_data_from('iconicity_ratings/iconicity_ratings_cleaned.csv')
    iconicity_model = IconicityModel(csv_data)
    
    # Create statistics by age group
    print("\nCreating age group statistics...")
    age_group_stats_raw = create_age_group_statistics(data_grouped_by_age, iconicity_model)
    
    # Process valid words by age group
    print("\nProcessing valid words by age group...")
    valid_words_stats = process_valid_words_by_age_group(age_group_stats_raw, iconicity_model)
    
    # Show valid word statistics
    print("\nValid word statistics by age group:")
    print_valid_words_statistics(valid_words_stats)

    # Export the valid statistics used by the plotter
    print("\nExporting valid_words_stats to JSON and CSV...")
    stats_exporter = ValidWordsStatsExporter("quarterly_valid_words")
    stats_exporter.export(valid_words_stats)

    # Create and show analysis plots
    print("\nCreating analysis plots...")
    plotter = DataAnalysisPlotter(valid_words_stats)
    
    # Create a directory for plots if it does not exist
    output_dir = 'iconic_vs_noniconic'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # General plot without percentages
    plotter.plot_iconic_vs_non_iconic_by_age(os.path.join(output_dir, 'iconic_vs_non_iconic_by_age.png'))
    
    # Separate plots with percentages
    plotter.plot_iconic_vs_non_iconic_by_age_adults(os.path.join(output_dir, 'iconic_vs_non_iconic_by_age_adults.png'))
    plotter.plot_iconic_vs_non_iconic_by_age_children(os.path.join(output_dir, 'iconic_vs_non_iconic_by_age_children.png'))
    
    # Show percentages of iconic and non-iconic words for adults
    print("\nIconic and non-iconic word percentages for adults by age group:")
    for age_group, stats in sorted(valid_words_stats.items()):
        total_adults = stats['adults']['total_words']
        iconic_pct = (stats['adults']['total_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
        non_iconic_pct = (stats['adults']['total_non_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
        print(f"\nAge group {age_group}:")
        print(f"  Iconic words: {iconic_pct:.1f}%")
        print(f"  Non-iconic words: {non_iconic_pct:.1f}%")

    # Create test directory and generate iconicity distribution plots
    print("\nGenerating iconicity distribution plots...")
    distribution_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "distribution",
    )
    os.makedirs(distribution_dir, exist_ok=True)
    plotter.plot_iconicity_distribution_by_age_group(save_dir=distribution_dir)

    # Generate iconicity distribution plot for all adult groups
    print("\nGenerating iconicity distribution plot for all adult groups...")
    plotter.plot_all_adults_iconicity_distribution(
        os.path.join(distribution_dir, "iconicity_distribution_all_adults.png")
    )

    # Generate iconicity distribution plot for all child groups
    print("\nGenerating iconicity distribution plot for all child groups...")
    plotter.plot_all_children_iconicity_distribution(
        os.path.join(distribution_dir, "iconicity_distribution_all_children.png")
    )

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
