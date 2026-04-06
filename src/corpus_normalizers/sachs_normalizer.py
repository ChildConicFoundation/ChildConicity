import os
import shutil

from src.corpus_normalizers.child_subdir_normalizer import (
    extract_age as _extract_age,
    modify_cha_file,
)

CHILD_NAME = "Naomi"
CORPUS_NAME = "Sachs"


def extract_age(file_path):
    return _extract_age(file_path, CORPUS_NAME)


def process_directory(source_dir, target_dir):
    os.makedirs(target_dir, exist_ok=True)

    target_subdir = os.path.join(target_dir, CHILD_NAME)
    os.makedirs(target_subdir, exist_ok=True)

    for file_name in sorted(os.listdir(source_dir)):
        if not file_name.endswith(".cha"):
            continue

        source_file = os.path.join(source_dir, file_name)
        target_file = os.path.join(target_subdir, file_name)
        shutil.copy2(source_file, target_file)

        age = extract_age(source_file)
        if age:
            modify_cha_file(target_file, CHILD_NAME, age)

        print(f"Copiado y modificado {source_file} a {target_file}")
