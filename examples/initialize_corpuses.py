import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corpus_initialization import (
    CorpusInitializer,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_SOURCE_ROOT,
)

def main(source_root=DEFAULT_SOURCE_ROOT, output_root=DEFAULT_OUTPUT_ROOT):
    """Wrapper de compatibilidad para inicializar todos los corpus."""
    initializer = CorpusInitializer(
        source_root=source_root,
        output_root=output_root,
    )
    initializer.initialize_all()

if __name__ == "__main__":
    main() 
