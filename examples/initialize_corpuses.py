import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corpus_initialization import (
    CorpusInitializer,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_SOURCE_ROOT,
)


def main(argv=None, source_root=DEFAULT_SOURCE_ROOT, output_root=DEFAULT_OUTPUT_ROOT):
    """Initialize all corpora from source_root into output_root."""
    if argv is not None:
        parser = argparse.ArgumentParser(
            description=(
                "Normalize TalkBank corpora from the source folder into the "
                "processed folder used by analyses."
            )
        )
        parser.add_argument(
            "--source-root",
            default=DEFAULT_SOURCE_ROOT,
            help=f"Folder with original corpora (default: {DEFAULT_SOURCE_ROOT}).",
        )
        parser.add_argument(
            "--output-root",
            default=DEFAULT_OUTPUT_ROOT,
            help=f"Folder for normalized corpora (default: {DEFAULT_OUTPUT_ROOT}).",
        )
        args = parser.parse_args(argv)
        source_root = args.source_root
        output_root = args.output_root

    initializer = CorpusInitializer(
        source_root=source_root,
        output_root=output_root,
    )
    initializer.initialize_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
