import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.initialize_corpuses import main as initialize_corpuses
from src.data_io.corpus_inspector import print_directory_structure, print_sampled_metadata
from src.data_io.grammatical_corpus_processing import (
    process_grammatical_data_with_formatter,
)
from src.data_io.reader import Reader
from src.quarterly_samples import GrammaticalCategoriesExporter, group_data_by_age


def main():
    print("Inicializando corpus...")
    initialize_corpuses()
    print("Corpus inicializados correctamente.")

    input_dir = "Corpus_modified"
    reader = Reader()
    corpus_data = reader.read_directory(input_dir)

    print("\nEstructura del corpus:")
    print_directory_structure(corpus_data)

    print("\nPrimeros 4 metadatos de cada archivo:")
    print_sampled_metadata(corpus_data)

    print("\nProcesando datos gramaticales con GrammaticalDataFormatter...")
    processed_data = process_grammatical_data_with_formatter(corpus_data)

    print("\nAgrupando datos gramaticales por edad...")
    data_grouped_by_age = group_data_by_age(processed_data)

    print("\nExportando categorías gramaticales a JSON y CSV...")
    exporter = GrammaticalCategoriesExporter("quarterly_grammatical_categories")
    exporter.export(data_grouped_by_age)

    print("\nProceso gramatical completado.")


if __name__ == "__main__":
    main()
