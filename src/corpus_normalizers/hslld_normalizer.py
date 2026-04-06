import os
import re
import shutil

from src.corpus_normalizers.child_subdir_normalizer import modify_cha_file

CORPUS_NAME = "HSLLD"
TARGET_CHILD_PATTERN = re.compile(
    r"@ID:\s*eng\|HSLLD\|CHI\|(\d+);(\d+)\.(\d*)\|.*?\|Target_Child\|\|\|"
)
CHILD_ID_PATTERN = re.compile(
    r"^(.+?)(?:fuzz|act|br|er|et|lw|md|mt|re|tp)\d+[a-z]*(?:pt\d+)?$"
)


def has_target_child(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return TARGET_CHILD_PATTERN.search(content) is not None


def extract_age(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = TARGET_CHILD_PATTERN.search(content)
    if match is None:
        return None

    years, months, days = match.groups()
    days = days if days else "0"
    return f"{years} years {months} months {days.zfill(2)} days"


def extract_child_name(file_path):
    stem = os.path.splitext(os.path.basename(file_path))[0]
    match = CHILD_ID_PATTERN.match(stem)
    if match is None:
        return None
    return match.group(1)


def process_directory(source_dir, target_dir):
    os.makedirs(target_dir, exist_ok=True)

    for root, _, files in os.walk(source_dir):
        for file_name in sorted(files):
            if not file_name.endswith(".cha"):
                continue

            source_file = os.path.join(root, file_name)
            if not has_target_child(source_file):
                print(f"Saltando archivo sin CHI objetivo: {source_file}")
                continue

            child_name = extract_child_name(source_file)
            age = extract_age(source_file)
            if child_name is None or age is None:
                print(f"Saltando archivo no normalizable: {source_file}")
                continue

            target_subdir = os.path.join(target_dir, child_name)
            os.makedirs(target_subdir, exist_ok=True)

            target_file = os.path.join(target_subdir, file_name)
            shutil.copy2(source_file, target_file)
            modify_cha_file(target_file, child_name, age)

            print(f"Copiado y modificado {source_file} a {target_file}")
