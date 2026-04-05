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
    """Función principal del programa"""
    parser = add_corpus_options(
        argparse.ArgumentParser(
            description=(
                "Procesa el corpus por tokens y permite filtrar qué corpus usar."
            )
        )
    )
    namespace = parser.parse_args(argv)
    corpus_options = CorpusCLIOptions.from_namespace(namespace)

    source_root = "Corpus"
    output_root = "Corpus_modified"

    # Inicializar los corpus
    print("Inicializando corpus...")
    initialize_corpuses(source_root=source_root, output_root=output_root)
    print("Corpus inicializados correctamente.")

    available_corpora = discover_available_corpora(output_root)
    corpus_options, should_exit = prepare_corpus_cli_options(
        corpus_options, available_corpora
    )
    if should_exit:
        return 0
    
    # Definir directorios de entrada y salida
    input_dir = output_root
    
    # Crear instancia del Reader
    reader = Reader()
    
    # Leer todos los directorios dentro del directorio procesado
    corpus_data = reader.read_directory(input_dir)
    corpus_data = filter_corpus_data(corpus_data, corpus_options.corpora)
    
    # Mostrar la estructura del diccionario anidado
    print("\nEstructura del corpus:")
    print_directory_structure(corpus_data)
    
    # Mostrar los primeros 4 metadatos de cada archivo
    print("\nPrimeros 4 metadatos de cada archivo:")
    print_sampled_metadata(corpus_data)
    
    # Procesar los datos usando DataFormatter
    print("\nProcesando datos con DataFormatter...")
    processed_data = process_data_with_formatter(corpus_data)
    
    # Agrupar datos por edad
    print("\nAgrupando datos por edad...")
    data_grouped_by_age = group_data_by_age(processed_data)

    # Crear el modelo de iconicidad
    print("\nCreando modelo de iconicidad...")
    formatter = DataFormatter()
    csv_data = formatter.format_csv_data_from('iconicity_ratings_cleaned.csv')
    iconicity_model = IconicityModel(csv_data)
    
    # Crear estadísticas por grupo de edad
    print("\nCreando estadísticas por grupo de edad...")
    age_group_stats_raw = create_age_group_statistics(data_grouped_by_age, iconicity_model)
    
    # Procesar palabras válidas por grupo de edad
    print("\nProcesando palabras válidas por grupo de edad...")
    valid_words_stats = process_valid_words_by_age_group(age_group_stats_raw, iconicity_model)
    
    # Mostrar estadísticas de palabras válidas
    print("\nMostrando estadísticas de palabras válidas por grupo de edad:")
    print_valid_words_statistics(valid_words_stats)

    # Exportar las estadísticas válidas que usa el plotter
    print("\nExportando valid_words_stats a JSON y CSV...")
    stats_exporter = ValidWordsStatsExporter("quarterly_valid_words")
    stats_exporter.export(valid_words_stats)

    # Crear y mostrar gráficas de análisis
    print("\nCreando gráficas de análisis...")
    plotter = DataAnalysisPlotter(valid_words_stats)
    
    # Crear directorio para las gráficas si no existe
    output_dir = 'iconic_vs_noniconic'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Gráfica general sin porcentajes
    plotter.plot_iconic_vs_non_iconic_by_age(os.path.join(output_dir, 'iconic_vs_non_iconic_by_age.png'))
    
    # Gráficas separadas con porcentajes
    plotter.plot_iconic_vs_non_iconic_by_age_adults(os.path.join(output_dir, 'iconic_vs_non_iconic_by_age_adults.png'))
    plotter.plot_iconic_vs_non_iconic_by_age_children(os.path.join(output_dir, 'iconic_vs_non_iconic_by_age_children.png'))
    
    # Mostrar porcentajes de palabras icónicas y no icónicas para adultos
    print("\nPorcentajes de palabras icónicas y no icónicas para adultos por grupo de edad:")
    for age_group, stats in sorted(valid_words_stats.items()):
        total_adults = stats['adults']['total_words']
        iconic_pct = (stats['adults']['total_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
        non_iconic_pct = (stats['adults']['total_non_iconic_occurrences'] / total_adults * 100) if total_adults > 0 else 0
        print(f"\nGrupo de edad {age_group}:")
        print(f"  Palabras icónicas: {iconic_pct:.1f}%")
        print(f"  Palabras no icónicas: {non_iconic_pct:.1f}%")

    # Crear directorio de pruebas y generar gráficas de distribución de iconicidad
    print("\nGenerando gráficas de distribución de iconicidad...")
    pruebas_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pruebas")
    os.makedirs(pruebas_dir, exist_ok=True)
    plotter.plot_iconicity_distribution_by_age_group(save_dir=pruebas_dir)
    
    # Generar gráfica de distribución de iconicidad para todos los grupos de adultos
    print("\nGenerando gráfica de distribución de iconicidad para todos los grupos de adultos...")
    plotter.plot_all_adults_iconicity_distribution(os.path.join(pruebas_dir, 'distribucion_iconicidad_todos_adultos.png'))

    # Generar gráfica de distribución de iconicidad para todos los grupos de niños
    print("\nGenerando gráfica de distribución de iconicidad para todos los grupos de niños...")
    plotter.plot_all_children_iconicity_distribution(os.path.join(pruebas_dir, 'distribucion_iconicidad_todos_ninos.png'))

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
