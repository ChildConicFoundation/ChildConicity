from collections import Counter


SPEAKER_GROUPS = {
    "adults": "adults_data",
    "children": "children_data",
}


def create_grammatical_type_stats(grouped_data, iconicity_model, grammatical_category=None):
    """
    Adapta los lemas de la capa %mor al formato que consume DataAnalysisPlotter.
    """
    iconicity_words = _build_iconicity_words(iconicity_model)
    selected_category = _normalize_category(grammatical_category)
    plotter_stats = {}

    for age_group, age_group_data in grouped_data.items():
        counters = _count_lemmas_by_speaker_group(age_group_data, selected_category)
        plotter_stats[age_group] = {
            speaker_group: _build_group_stats(counter, iconicity_words)
            for speaker_group, counter in counters.items()
        }

    return plotter_stats


def create_grammatical_type_stats_by_category(grouped_data, iconicity_model):
    iconicity_words = _build_iconicity_words(iconicity_model)
    categories = collect_grouped_grammatical_categories(grouped_data)
    stats_by_category = {category: {} for category in categories}

    for age_group, age_group_data in grouped_data.items():
        counters_by_category = {
            category: {speaker_group: Counter() for speaker_group in SPEAKER_GROUPS}
            for category in categories
        }

        for speaker_group, data_key in SPEAKER_GROUPS.items():
            for entry in age_group_data.get(data_key, {}).values():
                category = _normalize_category(entry.get("category"))
                lemma = _normalize_lemma(entry.get("lemma"))
                if not category or not lemma or category not in counters_by_category:
                    continue

                counters_by_category[category][speaker_group][lemma] += 1

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
                category = entry.get("category")
                if category:
                    categories.add(category)

    return sorted(categories)


def _count_lemmas_by_speaker_group(age_group_data, selected_category):
    counters = {speaker_group: Counter() for speaker_group in SPEAKER_GROUPS}

    for speaker_group, data_key in SPEAKER_GROUPS.items():
        for entry in age_group_data.get(data_key, {}).values():
            if not _should_include_entry(entry, selected_category):
                continue

            lemma = _normalize_lemma(entry.get("lemma"))
            if lemma:
                counters[speaker_group][lemma] += 1

    return counters


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


def _normalize_category(category):
    if category is None:
        return None

    return category.strip().casefold()


def _normalize_lemma(lemma):
    if not isinstance(lemma, str):
        return ""

    return lemma.strip().lower()
