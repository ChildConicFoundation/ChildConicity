from src.data_io.corpus_selection import (
    CORPUS_DATA_ROOT_KEY,
    TARGET_CORPORA,
    require_corpus_data_root,
)


def print_directory_structure(data, level=0):
    """
    Prints the directory structure visually.
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
                print("  " * (level + 1) + f"Name: {metadata.get('child_name', 'N/A')}")
                print("  " * (level + 1) + f"Age: {metadata.get('child_age', 'N/A')}")
                print(
                    "  " * (level + 1)
                    + f"Participants: {metadata.get('participants', 'N/A')}"
                )
                print("  " * (level + 1) + f"Types: {metadata.get('types', 'N/A')}")
                print()

        for key, value in content.items():
            if key != "files":
                print_metadata({key: value}, level + 1)


def print_sampled_metadata(data):
    """
    Prints metadata from 4 files for each corpus.
    """
    data = require_corpus_data_root(data)

    for corpus in TARGET_CORPORA:
        print(f"\n=== Corpus {corpus} ===")
        if corpus not in data[CORPUS_DATA_ROOT_KEY]:
            continue

        subdirs = list(data[CORPUS_DATA_ROOT_KEY][corpus].keys())
        if not subdirs:
            continue

        first_subdir = subdirs[0]
        corpus_branch = data[CORPUS_DATA_ROOT_KEY][corpus][first_subdir]
        if "files" not in corpus_branch:
            continue

        for file in corpus_branch["files"][:4]:
            print(f"\nFile: {file['metadata']['file_path']}")
            print(f"Child name: {file['metadata'].get('child_name', 'N/A')}")
            print(f"Age: {file['metadata'].get('child_age', 'N/A')}")
            print(f"Participants: {file['metadata'].get('participants', 'N/A')}")
            print(f"Types: {file['metadata'].get('types', 'N/A')}")
            if file["metadata"].get("utterances"):
                print(f"First utterance: {file['metadata']['utterances'][0]['text']}")
            print("-" * 50)


def show_lew_early_expressions(processed_data):
    """
    Shows Lew utterances when he was younger.
    """
    print("\n=== Lew early utterances ===")
    processed_data = require_corpus_data_root(processed_data)

    if "Post" not in processed_data[CORPUS_DATA_ROOT_KEY]:
        return
    if "Lew" not in processed_data[CORPUS_DATA_ROOT_KEY]["Post"]:
        return

    lew_files = processed_data[CORPUS_DATA_ROOT_KEY]["Post"]["Lew"]["files"]
    sorted_files = sorted(lew_files, key=lambda x: x["metadata"].get("child_age", ""))

    if not sorted_files:
        return

    oldest_file = sorted_files[0]
    print(f"\nFile: {oldest_file['metadata']['file_path']}")
    print(f"Age: {oldest_file['metadata'].get('child_age', 'N/A')}")
    print("\nFirst 20 Lew utterances:")

    for i, (_, entry) in enumerate(list(oldest_file["children_data"].items())[:20]):
        print(f"\n{i + 1}. {entry['text']}")
        if entry.get("timestamp"):
            print(f"   Time: {entry['timestamp']['start']}-{entry['timestamp']['end']}")
