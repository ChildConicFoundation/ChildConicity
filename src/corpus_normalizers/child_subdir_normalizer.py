import os
import re
import shutil


def extract_age(file_path, corpus_name):
    """Extrae la edad del archivo .cha."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Acepta edades completas (1;06.26) o sin día explícito (2;01.)
        match = re.search(
            rf"@ID:\s*eng\|{re.escape(corpus_name)}\|CHI\|(\d+);(\d+)\.(\d*)\|",
            content,
        )
        if match:
            years, months, days = match.groups()
            days = days if days else "0"
            return f"{years} years {months} months {days.zfill(2)} days"
    except FileNotFoundError:
        return None

    return None


def modify_cha_file(file_path, child_name, age):
    """Modifica el archivo .cha para añadir los metadatos normalizados."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    languages_pos = content.find("@Languages:")
    if languages_pos == -1:
        return

    end_of_line = content.find("\n", languages_pos)
    if end_of_line == -1:
        return

    new_content = (
        content[: end_of_line + 1]
        + f"@ChildName: {child_name}\n@ChildAge: {age}\n"
        + content[end_of_line + 1 :]
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def process_directory(source_dir, target_dir, corpus_name):
    """Procesa archivos .cha organizados por subcarpetas de niño."""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    subdirs = [
        d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))
    ]

    for subdir in subdirs:
        subdir_path = os.path.join(source_dir, subdir)
        target_subdir = os.path.join(target_dir, subdir)
        if not os.path.exists(target_subdir):
            os.makedirs(target_subdir)

        for file in os.listdir(subdir_path):
            if not file.endswith(".cha"):
                continue

            source_file = os.path.join(subdir_path, file)
            target_file = os.path.join(target_subdir, file)
            shutil.copy2(source_file, target_file)

            age = extract_age(source_file, corpus_name)
            if age:
                modify_cha_file(target_file, subdir, age)

            print(f"Copiado y modificado {source_file} a {target_file}")
