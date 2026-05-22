def get_age_quarter(age_str):
    """
    Convierte una cadena de edad en formato YYYYMMDD o
    "X years Y months Z days" a formato YYQ.

    Args:
        age_str (str): Edad en formato YYYYMMDD o "X years Y months Z days"

    Returns:
        str: Edad en formato YYQ (años y cuarto)
    """
    try:
        if "years" in age_str:
            parts = age_str.split()
            years = int(parts[0])
            months = int(parts[2])
        else:
            years = int(age_str[:2])
            months = int(age_str[2:4])

        quarter = ((months - 1) // 3) + 1
        quarter = min(max(quarter, 1), 4)

        return f"{years:02d}Y{quarter:02d}Q"
    except (ValueError, IndexError, TypeError):
        return "00Y00Q"


def group_data_by_age(processed_data):
    """
    Agrupa los datos por edad del niño en cuartos de año.

    Args:
        processed_data (dict): Datos procesados del corpus

    Returns:
        dict: Datos agrupados por edad en formato YYQ
    """
    data_grouped_by_age = {}
    processed_files = set()

    for _, corpus_data in processed_data["Corpora_modified"].items():
        for _, child_data in corpus_data.items():
            if "files" not in child_data:
                continue

            for file in child_data["files"]:
                file_path = file["metadata"]["file_path"]

                if file_path in processed_files:
                    continue
                processed_files.add(file_path)

                age = file["metadata"].get("child_age", "")
                if not age:
                    continue

                age_quarter = get_age_quarter(age)

                if age_quarter not in data_grouped_by_age:
                    data_grouped_by_age[age_quarter] = {
                        "children_data": {},
                        "other_children_data": {},
                        "adults_data": {},
                        "mlu_stats": _empty_mlu_stats(),
                        "files": [],
                    }

                child_base = len(data_grouped_by_age[age_quarter]["children_data"])
                other_child_base = len(
                    data_grouped_by_age[age_quarter]["other_children_data"]
                )
                adult_base = len(data_grouped_by_age[age_quarter]["adults_data"])

                for i, (_, utterance) in enumerate(file["children_data"].items()):
                    key = f"{child_base + i + 1}"
                    data_grouped_by_age[age_quarter]["children_data"][key] = (
                        _attach_file_metadata_to_entry(utterance, file["metadata"])
                    )

                for i, (_, utterance) in enumerate(
                    file.get("other_children_data", {}).items()
                ):
                    key = f"{other_child_base + i + 1}"
                    data_grouped_by_age[age_quarter]["other_children_data"][
                        key
                    ] = _attach_file_metadata_to_entry(utterance, file["metadata"])

                for i, (_, utterance) in enumerate(file["adults_data"].items()):
                    key = f"{adult_base + i + 1}"
                    data_grouped_by_age[age_quarter]["adults_data"][key] = (
                        _attach_file_metadata_to_entry(utterance, file["metadata"])
                    )

                _add_mlu_stats(
                    data_grouped_by_age[age_quarter]["mlu_stats"],
                    file["metadata"].get("mlu_stats", {}),
                )

                child_example = _build_entry_example(
                    file["children_data"], "No hay expresiones de niños"
                )
                other_child_example = _build_entry_example(
                    file.get("other_children_data", {}),
                    "No hay expresiones de otros niños",
                )
                adult_example = _build_entry_example(
                    file["adults_data"], "No hay expresiones de adultos"
                )

                data_grouped_by_age[age_quarter]["files"].append(
                    {
                        "file_path": file_path,
                        "child_name": file["metadata"].get("child_name", "N/A"),
                        "child_age": age,
                        "age_group": age_quarter,
                        "child_example": child_example,
                        "other_child_example": other_child_example,
                        "adult_example": adult_example,
                    }
                )

    return data_grouped_by_age


def _build_entry_example(entries, default_text):
    if not entries:
        return default_text

    first_entry = next(iter(entries.values()))
    if "text" in first_entry:
        return first_entry["text"]

    category = first_entry.get("category", "")
    lemma = first_entry.get("lemma", "")
    attributes = "-".join(first_entry.get("attributes", []))

    if attributes:
        return f"{category}|{lemma}-{attributes}"
    return f"{category}|{lemma}"


def _attach_file_metadata_to_entry(entry, metadata):
    enriched_entry = entry.copy()
    enriched_entry["child_name"] = metadata.get("child_name", "N/A")
    enriched_entry["file_path"] = metadata.get("file_path", "")
    return enriched_entry


def _empty_mlu_stats():
    return {
        "children": {"morpheme_count": 0, "utterance_count": 0},
        "other_children": {"morpheme_count": 0, "utterance_count": 0},
        "adults": {"morpheme_count": 0, "utterance_count": 0},
    }


def _add_mlu_stats(target, source):
    for speaker_group, group_stats in source.items():
        if speaker_group not in target:
            continue

        target[speaker_group]["morpheme_count"] += group_stats.get(
            "morpheme_count", 0
        )
        target[speaker_group]["utterance_count"] += group_stats.get(
            "utterance_count", 0
        )
