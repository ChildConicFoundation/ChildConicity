from collections import Counter


TYPE_COUNT_WITH_REPETITIONS = "with_repetitions"
TYPE_COUNT_ONLY_ONCE = "only_once"
TYPE_COUNT_MODES = {
    TYPE_COUNT_WITH_REPETITIONS,
    TYPE_COUNT_ONLY_ONCE,
}
DEFAULT_TYPE_COUNT_MODE = TYPE_COUNT_WITH_REPETITIONS

SPEAKER_GROUPS = {
    "adults": "adults_data",
    "children": "children_data",
}


def create_grammatical_type_stats(
    grouped_data,
    iconicity_model,
    grammatical_category=None,
    count_mode=DEFAULT_TYPE_COUNT_MODE,
):
    """
    Adapta los lemas de la capa %mor al formato que consume DataAnalysisPlotter.
    """
    iconicity_words = _build_iconicity_words(iconicity_model)
    selected_category = _normalize_category(grammatical_category)
    selected_count_mode = normalize_type_count_mode(count_mode)
    plotter_stats = {}

    for age_group, age_group_data in grouped_data.items():
        counters = _count_lemmas_by_speaker_group(
            age_group_data,
            selected_category,
            selected_count_mode,
        )
        plotter_stats[age_group] = {
            speaker_group: _build_group_stats(counter, iconicity_words)
            for speaker_group, counter in counters.items()
        }

    return plotter_stats


def create_grammatical_type_stats_by_category(
    grouped_data,
    iconicity_model,
    count_mode=DEFAULT_TYPE_COUNT_MODE,
):
    iconicity_words = _build_iconicity_words(iconicity_model)
    categories = collect_grouped_grammatical_categories(grouped_data)
    selected_count_mode = normalize_type_count_mode(count_mode)
    stats_by_category = {category: {} for category in categories}

    for age_group, age_group_data in grouped_data.items():
        counters_by_category = {
            category: {speaker_group: Counter() for speaker_group in SPEAKER_GROUPS}
            for category in categories
        }

        for speaker_group, data_key in SPEAKER_GROUPS.items():
            entry_counts = _count_entry_identities(
                age_group_data.get(data_key, {}).values()
            )
            for (
                category,
                lemma,
                _attributes,
                _raw_token,
            ), count in entry_counts.items():
                if not category or not lemma or category not in counters_by_category:
                    continue

                counters_by_category[category][speaker_group][lemma] += _count_weight(
                    count,
                    selected_count_mode,
                )

        for category in categories:
            stats_by_category[category][age_group] = {
                speaker_group: _build_group_stats(counter, iconicity_words)
                for speaker_group, counter in counters_by_category[category].items()
            }

    return stats_by_category


def collect_grouped_grammatical_categories(grouped_data):
    categories = set()

    for age_group_data in grouped_data.values():
        for data_key in SPEAKER_GROUPS.values():
            for entry in age_group_data.get(data_key, {}).values():
                category = _normalize_category(entry.get("category"))
                if category:
                    categories.add(category)

    return sorted(categories)


def _count_lemmas_by_speaker_group(age_group_data, selected_category, count_mode):
    counters = {speaker_group: Counter() for speaker_group in SPEAKER_GROUPS}

    for speaker_group, data_key in SPEAKER_GROUPS.items():
        entry_counts = _count_entry_identities(
            age_group_data.get(data_key, {}).values(),
            selected_category=selected_category,
        )

        for (_category, lemma, _attributes, _raw_token), count in entry_counts.items():
            counters[speaker_group][lemma] += _count_weight(count, count_mode)

    return counters


def _count_entry_identities(entries, selected_category=None):
    entry_counts = Counter()

    for entry in entries:
        if not _should_include_entry(entry, selected_category):
            continue

        lemma = _normalize_lemma(entry.get("lemma"))
        if not lemma:
            continue

        repetition_count = _entry_repetition_count(entry)
        if repetition_count <= 0:
            continue

        entry_counts[_entry_identity(entry, lemma)] += repetition_count

    return entry_counts


def _entry_identity(entry, lemma):
    return (
        _normalize_category(entry.get("category")) or "",
        lemma,
        _normalize_attributes(entry.get("attributes", [])),
        _normalize_raw_token(entry.get("raw_token")),
    )


def _normalize_attributes(attributes):
    if isinstance(attributes, str):
        return tuple(part.strip() for part in attributes.split("|") if part.strip())

    if isinstance(attributes, (list, tuple)):
        return tuple(
            str(attribute).strip()
            for attribute in attributes
            if str(attribute).strip()
        )

    return ()


def _normalize_raw_token(raw_token):
    if not isinstance(raw_token, str):
        return ""

    return raw_token.strip()


def _entry_repetition_count(entry):
    try:
        count = int(entry.get("count", 1))
    except (TypeError, ValueError):
        return 1

    return max(count, 0)


def _count_weight(count, count_mode):
    if count_mode == TYPE_COUNT_ONLY_ONCE:
        return 1

    return count


def _build_iconicity_words(iconicity_model):
    return {
        normalized_word: word_data
        for word, word_data in iconicity_model.get_all_word_data().items()
        if (normalized_word := _normalize_lemma(word))
    }


def _build_group_stats(counter, iconicity_words):
    group_stats = {
        "total_words": 0,
        "iconic_words": {},
        "non_iconic_words": {},
        "total_iconic_occurrences": 0,
        "total_non_iconic_occurrences": 0,
        "unique_iconic_words": set(),
        "unique_non_iconic_words": set(),
    }

    for lemma, count in sorted(counter.items()):
        group_stats["total_words"] += count
        if lemma in iconicity_words:
            group_stats["iconic_words"][lemma] = {
                "count": count,
                "rating": iconicity_words[lemma]["rating"],
            }
            group_stats["total_iconic_occurrences"] += count
            group_stats["unique_iconic_words"].add(lemma)
        else:
            group_stats["non_iconic_words"][lemma] = count
            group_stats["total_non_iconic_occurrences"] += count
            group_stats["unique_non_iconic_words"].add(lemma)

    return group_stats


def _should_include_entry(entry, selected_category):
    if selected_category is None:
        return True

    return _normalize_category(entry.get("category")) == selected_category


def normalize_type_count_mode(count_mode):
    if count_mode in TYPE_COUNT_MODES:
        return count_mode

    return DEFAULT_TYPE_COUNT_MODE


def _normalize_category(category):
    if category is None:
        return None

    return category.strip().casefold()


def _normalize_lemma(lemma):
    if not isinstance(lemma, str):
        return ""

    return lemma.strip().lower()
