from src.corpus_normalizers.child_subdir_normalizer import process_directory as _process


def process_directory(source_dir, target_dir):
    _process(source_dir, target_dir, "Brown")
