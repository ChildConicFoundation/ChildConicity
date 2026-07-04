import os
import shutil
import tempfile
from dataclasses import dataclass

from src.corpus_normalizers.bates_normalizer import process_directory as process_bates
from src.corpus_normalizers.bloom_normalizer import process_directory as process_bloom
from src.corpus_normalizers.brown_normalizer import process_directory as process_brown
from src.corpus_normalizers.brent_normalizer import BrendManipulator
from src.corpus_normalizers.hslld_normalizer import process_directory as process_hslld
from src.corpus_normalizers.kuczaj_normalizer import process_directory as process_kuczaj
from src.corpus_normalizers.newengland_normalizer import (
    process_directory as process_newengland,
)
from src.corpus_normalizers.post_normalizer import process_directory as process_post
from src.corpus_normalizers.sachs_normalizer import process_directory as process_sachs
from src.corpus_normalizers.providence_normalizer import (
    process_directory as process_providence,
)
from src.corpus_normalizers.vankleeck_normalizer import (
    process_directory as process_vankleeck,
)

DEFAULT_SOURCE_ROOT = "Corpora"
DEFAULT_OUTPUT_ROOT = "Corpora_modified"


@dataclass
class CorpusInitializer:
    source_root: str = DEFAULT_SOURCE_ROOT
    output_root: str = DEFAULT_OUTPUT_ROOT

    def initialize_bates(self):
        """Initializes the Bates corpus."""
        self._initialize_corpus("Bates", process_bates)

    def initialize_brent(self):
        """Initializes the Brent corpus."""
        print("\nInitializing Brent...")

        manipulator = BrendManipulator()
        manipulator.base_dir = self._source_dir("Brent")
        manipulator.output_dir = self._prepare_output_dir("Brent")
        try:
            manipulator.process_directory()
        except Exception:
            self._discard_pending_output("Brent")
            raise
        self._commit_pending_output("Brent")

        print("Brent corpus initialized!")

    def initialize_new_england(self):
        """Initializes the NewEngland corpus."""
        self._initialize_corpus("NewEngland", process_newengland)

    def initialize_post(self):
        """Initializes the Post corpus."""
        self._initialize_corpus("Post", process_post)

    def initialize_bloom(self):
        """Initializes the Bloom corpus."""
        self._initialize_corpus("Bloom", process_bloom)

    def initialize_brown(self):
        """Initializes the Brown corpus."""
        self._initialize_corpus("Brown", process_brown)

    def initialize_hslld(self):
        """Initializes the HSLLD corpus."""
        self._initialize_corpus("HSLLD", process_hslld)

    def initialize_kuczaj(self):
        """Initializes the Kuczaj corpus."""
        self._initialize_corpus("Kuczaj", process_kuczaj)

    def initialize_sachs(self):
        """Initializes the Sachs corpus."""
        self._initialize_corpus("Sachs", process_sachs)

    def initialize_van_kleeck(self):
        """Initializes the VanKleeck corpus."""
        self._initialize_corpus("VanKleeck", process_vankleeck)

    def initialize_providence(self):
        """Initializes the Providence corpus."""
        self._initialize_corpus("Providence", process_providence)

    def initialize_all(self):
        """Initializes all corpora."""
        print("Starting corpus initialization...")
        self.initialize_bates()
        self.initialize_brent()
        self.initialize_new_england()
        self.initialize_post()
        self.initialize_bloom()
        self.initialize_brown()
        self.initialize_hslld()
        self.initialize_kuczaj()
        self.initialize_sachs()
        self.initialize_van_kleeck()
        self.initialize_providence()
        print("\nCorpus initialization completed!")

    def _source_dir(self, corpus_name):
        return os.path.join(self.source_root, corpus_name)

    def _output_dir(self, corpus_name):
        return os.path.join(self.output_root, corpus_name)

    def _initialize_corpus(self, corpus_name, processor):
        print(f"\nInitializing {corpus_name}...")
        output_dir = self._prepare_output_dir(corpus_name)
        try:
            processor(self._source_dir(corpus_name), output_dir)
        except Exception:
            self._discard_pending_output(corpus_name)
            raise
        self._commit_pending_output(corpus_name)
        print(f"{corpus_name} corpus initialized!")

    def _prepare_output_dir(self, corpus_name):
        os.makedirs(self.output_root, exist_ok=True)
        pending_dir = self._pending_output_dir(corpus_name)
        if os.path.exists(pending_dir):
            shutil.rmtree(pending_dir)
        os.makedirs(pending_dir, exist_ok=True)
        return pending_dir

    def _commit_pending_output(self, corpus_name):
        output_dir = self._output_dir(corpus_name)
        pending_dir = self._pending_output_dir(corpus_name)
        backup_dir = None
        if os.path.exists(output_dir):
            backup_dir = tempfile.mkdtemp(
                dir=self.output_root,
                prefix=f".{corpus_name}.previous.",
            )
            os.rmdir(backup_dir)
            os.replace(output_dir, backup_dir)
        try:
            os.replace(pending_dir, output_dir)
        except Exception:
            if backup_dir and os.path.exists(backup_dir):
                os.replace(backup_dir, output_dir)
            raise
        if backup_dir and os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)

    def _discard_pending_output(self, corpus_name):
        pending_dir = self._pending_output_dir(corpus_name)
        if os.path.exists(pending_dir):
            shutil.rmtree(pending_dir)

    def _pending_output_dir(self, corpus_name):
        return os.path.join(self.output_root, f".{corpus_name}.pending")
