from src.corpus_normalizers.child_subdir_normalizer import (
    extract_age as _extract_age,
)
from src.corpus_normalizers.child_subdir_normalizer import (
    modify_cha_file,
    process_directory as _process_directory,
)

CORPUS_NAME = "Bloom"


def extract_age(file_path):
    return _extract_age(file_path, CORPUS_NAME)


def process_directory(source_dir, target_dir):
    return _process_directory(source_dir, target_dir, CORPUS_NAME)
