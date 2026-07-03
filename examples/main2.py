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
                "Procesa el corpus por tokens y permite filtrar qué corpus usar."
            )
        )
    )
    namespace = parser.parse_args(argv)
    corpus_options = CorpusCLIOptions.from_namespace(namespace)

    source_root = "Corpora"
    output_root = "Corpora_modified"

    # Initialize corpora
    print("Inicializando corpus...")
    initialize_corpuses(source_root=source_root, output_root=output_root)
    print("Corpus inicializados correctamente.")

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
    print("\nEstructura del corpus:")
    print_directory_structure(corpus_data)
    
    # Show the first 4 metadata entries for each file
    print("\nPrimeros 4 metadatos de cada archivo:")
    print_sampled_metadata(corpus_data)
    
    # Process the data using DataFormatter
    print("\nProcesando datos con DataFormatter...")
    processed_data = process_data_with_formatter(corpus_data)
    
    # Group data by age
    print("\nAgrupando datos por edad...")
    data_grouped_by_age = group_data_by_age(processed_data)

    # Create the iconicity model
    print("\nCreando modelo de iconicidad...")
    formatter = DataFormatter()
    csv_data = formatter.format_csv_data_from('iconicity_ratings/iconicity_ratings_cleaned.csv')
    iconicity_model = IconicityModel(csv_data)
    
    # Create statistics by age group
    print("\nCreando estadísticas por grupo de edad...")
    age_group_stats_raw = create_age_group_statistics(data_grouped_by_age, iconicity_model)
    
    # Process valid words by age group
    print("\nProcesando palabras válidas por grupo de edad...")
    valid_words_stats = process_valid_words_by_age_group(age_group_stats_raw, iconicity_model)
    
    # Show valid word statistics
    print("\nMostrando estadísticas de palabras válidas por grupo de edad:")
    print_valid_words_statistics(valid_words_stats)

    # Export the valid statistics used by the plotter
    print("\nExportando valid_words_stats a JSON y CSV...")
    stats_exporter = ValidWordsStatsExporter("quarterly_valid_words")
    stats_exporter.export(valid_words_stats)

    # Create and show analysis plots
    print("\nCreando gráficas de análisis...")
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
    print("\nPorcentajes de palabras icónicas y no icónicas para adultos por grupo de edad:")
    for age_group, stats in sorted(valid_words_stats.items()):
        total_adults = stats['adults']['total_words']
        iconic_pct = (stats['adults']['total_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
        non_iconic_pct = (stats['adults']['total_non_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
        print(f"\nGrupo de edad {age_group}:")
        print(f"  Palabras icónicas: {iconic_pct:.1f}%")
        print(f"  Palabras no icónicas: {non_iconic_pct:.1f}%")

    # Create test directory and generate iconicity distribution plots
    print("\nGenerando gráficas de distribución de iconicidad...")
    pruebas_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pruebas")
    os.makedirs(pruebas_dir, exist_ok=True)
    plotter.plot_iconicity_distribution_by_age_group(save_dir=pruebas_dir)
    
    # Generate iconicity distribution plot for all adult groups
    print("\nGenerando gráfica de distribución de iconicidad para todos los grupos de adultos...")
    plotter.plot_all_adults_iconicity_distribution(os.path.join(pruebas_dir, 'distribucion_iconicidad_todos_adultos.png'))

    # Generate iconicity distribution plot for all child groups
    print("\nGenerando gráfica de distribución de iconicidad para todos los grupos de niños...")
    plotter.plot_all_children_iconicity_distribution(os.path.join(pruebas_dir, 'distribucion_iconicidad_todos_ninos.png'))

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
