import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.initialize_corpuses import main as initialize_corpuses
from src.cli import parse_grammatical_cli_options, prepare_grammatical_cli_options
from src.data_io.corpus_inspector import print_directory_structure, print_sampled_metadata
from src.data_io.grammatical_corpus_processing import (
    collect_grammatical_categories,
    run_grammatical_pipeline,
)
from src.data_io.reader import Reader


def main(argv=None):
    options = parse_grammatical_cli_options(argv)
    source_root = "Corpus"
    output_root = "Corpus_modified"

    print("Inicializando corpus...")
    initialize_corpuses(source_root=source_root, output_root=output_root)
    print("Corpus inicializados correctamente.")

    input_dir = output_root
    reader = Reader()
    corpus_data = reader.read_directory(input_dir)

    available_categories = collect_grammatical_categories(corpus_data)
    options, should_exit = prepare_grammatical_cli_options(
        options, available_categories
    )
    if should_exit:
        return 0

    selected_categories = options.categories

    print("\nEstructura del corpus:")
    print_directory_structure(corpus_data)

    print("\nPrimeros 4 metadatos de cada archivo:")
    print_sampled_metadata(corpus_data)

    print("\nProcesando datos gramaticales y exportando resultados...")
    run_grammatical_pipeline(
        corpus_data,
        output_dir=options.output_dir,
        grammatical_categories=selected_categories,
    )

    print("\nProceso gramatical completado.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
