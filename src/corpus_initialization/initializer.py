import os
from dataclasses import dataclass

from src.corpus_normalizers.bloom_normalizer import process_directory as process_bloom
from src.corpus_normalizers.brown_normalizer import process_directory as process_brown
from src.corpus_normalizers.brent_normalizer import BrendManipulator
from src.corpus_normalizers.hslld_normalizer import process_directory as process_hslld
from src.corpus_normalizers.newengland_normalizer import (
    process_directory as process_newengland,
)
from src.corpus_normalizers.post_normalizer import process_directory as process_post
from src.corpus_normalizers.vankleeck_normalizer import (
    process_directory as process_vankleeck,
)

DEFAULT_SOURCE_ROOT = "Corpus"
DEFAULT_OUTPUT_ROOT = "Corpus_modified"


@dataclass
class CorpusInitializer:
    source_root: str = DEFAULT_SOURCE_ROOT
    output_root: str = DEFAULT_OUTPUT_ROOT

    def initialize_brent(self):
        """Inicializa el corpus de Brent."""
        print("\nInicializando corpus de Brent...")

        manipulator = BrendManipulator()
        manipulator.base_dir = self._source_dir("Brent")
        manipulator.output_dir = self._output_dir("Brent")
        manipulator.process_directory()

        print("¡Corpus de Brent inicializado!")

    def initialize_new_england(self):
        """Inicializa el corpus de NewEngland."""
        print("\nInicializando corpus de NewEngland...")
        process_newengland(self._source_dir("NewEngland"), self._output_dir("NewEngland"))
        print("¡Corpus de NewEngland inicializado!")

    def initialize_post(self):
        """Inicializa el corpus de Post."""
        print("\nInicializando corpus de Post...")
        process_post(self._source_dir("Post"), self._output_dir("Post"))
        print("¡Corpus de Post inicializado!")

    def initialize_bloom(self):
        """Inicializa el corpus de Bloom."""
        print("\nInicializando corpus de Bloom...")
        process_bloom(
            self._source_dir("Bloom"),
            self._output_dir("Bloom"),
        )
        print("¡Corpus de Bloom inicializado!")

    def initialize_brown(self):
        """Inicializa el corpus de Brown."""
        print("\nInicializando corpus de Brown...")
        process_brown(
            self._source_dir("Brown"),
            self._output_dir("Brown"),
        )
        print("¡Corpus de Brown inicializado!")

    def initialize_hslld(self):
        """Inicializa el corpus de HSLLD."""
        print("\nInicializando corpus de HSLLD...")
        process_hslld(
            self._source_dir("HSLLD"),
            self._output_dir("HSLLD"),
        )
        print("¡Corpus de HSLLD inicializado!")

    def initialize_van_kleeck(self):
        """Inicializa el corpus de VanKleeck."""
        print("\nInicializando corpus de VanKleeck...")
        process_vankleeck(self._source_dir("VanKleeck"), self._output_dir("VanKleeck"))
        print("¡Corpus de VanKleeck inicializado!")

    def initialize_all(self):
        """Inicializa todos los corpus."""
        print("Iniciando inicialización de corpus...")
        self.initialize_brent()
        self.initialize_new_england()
        self.initialize_post()
        self.initialize_bloom()
        self.initialize_brown()
        self.initialize_hslld()
        self.initialize_van_kleeck()
        print("\n¡Inicialización de corpus completada!")

    def _source_dir(self, corpus_name):
        return os.path.join(self.source_root, corpus_name)

    def _output_dir(self, corpus_name):
        return os.path.join(self.output_root, corpus_name)
