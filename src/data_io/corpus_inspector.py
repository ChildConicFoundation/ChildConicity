def print_directory_structure(data, level=0):
    """
    Imprime la estructura del directorio de forma visual.
    """
    for dir_name, content in data.items():
        print("  " * level + "📁 " + dir_name)

        if "files" in content:
            for file in content["files"]:
                print("  " * (level + 1) + "📄 " + file["metadata"]["file_path"])

        for key, value in content.items():
            if key != "files":
                print_directory_structure({key: value}, level + 1)


def print_metadata(data, level=0):
    for _, content in data.items():
        if "files" in content:
            for file in content["files"]:
                print("  " * level + "📄 " + file["metadata"]["file_path"])
                metadata = file["metadata"]
                print("  " * (level + 1) + f"Nombre: {metadata.get('child_name', 'N/A')}")
                print("  " * (level + 1) + f"Edad: {metadata.get('child_age', 'N/A')}")
                print(
                    "  " * (level + 1)
                    + f"Participantes: {metadata.get('participants', 'N/A')}"
                )
                print("  " * (level + 1) + f"Tipos: {metadata.get('types', 'N/A')}")
                print()

        for key, value in content.items():
            if key != "files":
                print_metadata({key: value}, level + 1)


def print_sampled_metadata(data):
    """
    Imprime los metadatos de 4 archivos de cada corpus.
    """
    main_dirs = ["Brent", "NewEngland", "Post", "Bloom", "Brown", "HSLLD", "Kuczaj", "Sachs", "VanKleeck"]

    for corpus in main_dirs:
        print(f"\n=== Corpus {corpus} ===")
        if corpus not in data["Corpus_modified"]:
            continue

        subdirs = list(data["Corpus_modified"][corpus].keys())
        if not subdirs:
            continue

        first_subdir = subdirs[0]
        corpus_branch = data["Corpus_modified"][corpus][first_subdir]
        if "files" not in corpus_branch:
            continue

        for file in corpus_branch["files"][:4]:
            print(f"\nArchivo: {file['metadata']['file_path']}")
            print(f"Nombre del niño: {file['metadata'].get('child_name', 'N/A')}")
            print(f"Edad: {file['metadata'].get('child_age', 'N/A')}")
            print(f"Participantes: {file['metadata'].get('participants', 'N/A')}")
            print(f"Tipos: {file['metadata'].get('types', 'N/A')}")
            if file["metadata"].get("utterances"):
                print(f"Primera expresión: {file['metadata']['utterances'][0]['text']}")
            print("-" * 50)


def show_lew_early_expressions(processed_data):
    """
    Muestra las expresiones de Lew cuando era más joven.
    """
    print("\n=== Expresiones tempranas de Lew ===")

    if "Post" not in processed_data["Corpus_modified"]:
        return
    if "Lew" not in processed_data["Corpus_modified"]["Post"]:
        return

    lew_files = processed_data["Corpus_modified"]["Post"]["Lew"]["files"]
    sorted_files = sorted(lew_files, key=lambda x: x["metadata"].get("child_age", ""))

    if not sorted_files:
        return

    oldest_file = sorted_files[0]
    print(f"\nArchivo: {oldest_file['metadata']['file_path']}")
    print(f"Edad: {oldest_file['metadata'].get('child_age', 'N/A')}")
    print("\nPrimeras 20 expresiones de Lew:")

    for i, (_, entry) in enumerate(list(oldest_file["children_data"].items())[:20]):
        print(f"\n{i + 1}. {entry['text']}")
        if entry.get("timestamp"):
            print(f"   Tiempo: {entry['timestamp']['start']}-{entry['timestamp']['end']}")
