import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.initialize_corpuses import main as initialize_corpuses
from src.cli import (
    CorpusCLIOptions,
    GrammaticalCLIOptions,
    add_corpus_options,
    build_grammatical_options_parser,
    prepare_corpus_cli_options,
    prepare_grammatical_cli_options,
)
from src.data_io.corpus_inspector import print_directory_structure, print_sampled_metadata
from src.data_io.grammatical_corpus_processing import (
    collect_grammatical_categories,
    run_grammatical_pipeline,
)
from src.data_io.reader import Reader
from src.data_io.corpus_selection import (
    discover_available_corpora,
    filter_corpus_data,
)


def main(argv=None):
    parser = build_grammatical_options_parser()
    add_corpus_options(parser)
    namespace = parser.parse_args(argv)
    options = GrammaticalCLIOptions.from_namespace(namespace)
    corpus_options = CorpusCLIOptions.from_namespace(namespace)
    source_root = "Corpora"
    output_root = "Corpora_modified"

    print("Initializing corpora...")
    initialize_corpuses(source_root=source_root, output_root=output_root)
    print("Corpora initialized successfully.")

    available_corpora = discover_available_corpora(output_root)
    corpus_options, should_exit = prepare_corpus_cli_options(
        corpus_options, available_corpora
    )
    if should_exit:
        return 0

    input_dir = output_root
    reader = Reader()
    corpus_data = reader.read_directory(input_dir)
    corpus_data = filter_corpus_data(corpus_data, corpus_options.corpora)

    available_categories = collect_grammatical_categories(corpus_data)
    options, should_exit = prepare_grammatical_cli_options(
        options, available_categories
    )
    if should_exit:
        return 0

    selected_categories = options.categories

    print("\nCorpus structure:")
    print_directory_structure(corpus_data)

    print("\nFirst 4 metadata entries per file:")
    print_sampled_metadata(corpus_data)

    print("\nProcessing grammatical data and exporting results...")
    run_grammatical_pipeline(
        corpus_data,
        output_dir=options.output_dir,
        grammatical_categories=selected_categories,
    )

    print("\nGrammatical processing completed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
