import os
import re
import shutil

from src.corpus_normalizers.child_subdir_normalizer import (
    extract_age as _extract_age,
    modify_cha_file,
)

CORPUS_NAME = "Bates"

# Strips session suffixes from filenames: amy28→amy, amyst→amy, ed_snack→ed
_SUFFIX = re.compile(r"(28$|st$|_.*$)")


def _child_name(stem):
    base = _SUFFIX.sub("", stem).strip()
    return (base if base else stem).capitalize()


def extract_age(file_path):
    return _extract_age(file_path, CORPUS_NAME)


def process_directory(source_dir, target_dir):
    os.makedirs(target_dir, exist_ok=True)

    session_dirs = [
        d for d in os.listdir(source_dir)
        if os.path.isdir(os.path.join(source_dir, d))
    ]

    for session in session_dirs:
        src_session = os.path.join(source_dir, session)
        tgt_session = os.path.join(target_dir, session)
        os.makedirs(tgt_session, exist_ok=True)

        for fname in os.listdir(src_session):
            if not fname.endswith(".cha"):
                continue

            src_file = os.path.join(src_session, fname)
            tgt_file = os.path.join(tgt_session, fname)
            shutil.copy2(src_file, tgt_file)

            child_name = _child_name(os.path.splitext(fname)[0])
            age = extract_age(src_file)
            if age:
                modify_cha_file(tgt_file, child_name, age)

            print(f"Copied and modified {src_file} to {tgt_file}")
