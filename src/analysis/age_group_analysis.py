from src.analysis.word_counter import WordCounter


def create_age_group_statistics(data_grouped_by_age, iconicity_model):
    """
    Creates a dictionary with word and iconicity statistics by age group.
    """
    age_group_stats = {}
    all_iconicity_words = iconicity_model.get_all_word_data()

    for age_group, data in data_grouped_by_age.items():
        children_counter = WordCounter()
        adults_counter = WordCounter()

        for utterance in data["children_data"].values():
            children_counter.count_words(utterance["text"])

        for utterance in data["adults_data"].values():
            adults_counter.count_words(utterance["text"])

        age_group_stats[age_group] = {
            "age_group": age_group,
            "children_counted_words": children_counter.get_word_counts(),
            "adults_counted_words": adults_counter.get_word_counts(),
            "all_iconicity_words": all_iconicity_words,
        }

    return age_group_stats


def print_age_group_statistics(age_group_stats, num_words=10):
    """
    Prints word statistics by age group.
    """
    for age_group, stats in sorted(age_group_stats.items()):
        print(f"\n=== Age group {age_group} ===")

        print("\nTop child words:")
        children_words = sorted(
            stats["children_counted_words"].items(), key=lambda x: x[1], reverse=True
        )[:num_words]
        for word, count in children_words:
            print(f"  {word}: {count}")

        print("\nTop adult words:")
        adults_words = sorted(
            stats["adults_counted_words"].items(), key=lambda x: x[1], reverse=True
        )[:num_words]
        for word, count in adults_words:
            print(f"  {word}: {count}")

        children_iconic = set(
            word
            for word in stats["children_counted_words"].keys()
            if word in stats["all_iconicity_words"]
        )
        adults_iconic = set(
            word
            for word in stats["adults_counted_words"].keys()
            if word in stats["all_iconicity_words"]
        )

        print("\nIconicity statistics:")
        print(f"  Iconic words used by children: {len(children_iconic)}")
        print(f"  Iconic words used by adults: {len(adults_iconic)}")
        print("-" * 50)


def process_valid_words_by_age_group(age_group_stats, iconicity_model):
    """
    Processes valid words by age group, classifying them as iconic or non-iconic.
    """
    valid_words_stats = {}
    all_iconicity_words = iconicity_model.get_all_word_data()

    for age_group, stats in age_group_stats.items():
        group_stats = {
            "adults": {
                "total_words": 0,
                "iconic_words": {},
                "non_iconic_words": {},
                "total_iconic_occurrences": 0,
                "total_non_iconic_occurrences": 0,
                "unique_iconic_words": set(),
                "unique_non_iconic_words": set(),
            },
            "children": {
                "total_words": 0,
                "iconic_words": {},
                "non_iconic_words": {},
                "total_iconic_occurrences": 0,
                "total_non_iconic_occurrences": 0,
                "unique_iconic_words": set(),
                "unique_non_iconic_words": set(),
            },
        }

        for word, count_data in stats["adults_counted_words"].items():
            count = count_data["count"]
            group_stats["adults"]["total_words"] += count
            if word in all_iconicity_words:
                group_stats["adults"]["iconic_words"][word] = {
                    "count": count,
                    "rating": all_iconicity_words[word]["rating"],
                }
                group_stats["adults"]["total_iconic_occurrences"] += count
                group_stats["adults"]["unique_iconic_words"].add(word)
            else:
                group_stats["adults"]["non_iconic_words"][word] = count
                group_stats["adults"]["total_non_iconic_occurrences"] += count
                group_stats["adults"]["unique_non_iconic_words"].add(word)

        for word, count_data in stats["children_counted_words"].items():
            count = count_data["count"]
            group_stats["children"]["total_words"] += count
            if word in all_iconicity_words:
                group_stats["children"]["iconic_words"][word] = {
                    "count": count,
                    "rating": all_iconicity_words[word]["rating"],
                }
                group_stats["children"]["total_iconic_occurrences"] += count
                group_stats["children"]["unique_iconic_words"].add(word)
            else:
                group_stats["children"]["non_iconic_words"][word] = count
                group_stats["children"]["total_non_iconic_occurrences"] += count
                group_stats["children"]["unique_non_iconic_words"].add(word)

        valid_words_stats[age_group] = group_stats

    return valid_words_stats


def print_valid_words_statistics(valid_words_stats):
    """
    Prints valid word statistics by age group.
    """
    for age_group, stats in sorted(valid_words_stats.items()):
        print(f"\n=== Age group {age_group} ===")

        print("\nAdult statistics:")
        print(f"  Total words: {stats['adults']['total_words']}")

        total_iconic_occurrences_adults = stats["adults"]["total_iconic_occurrences"]
        total_non_iconic_occurrences_adults = stats["adults"][
            "total_non_iconic_occurrences"
        ]

        print(
            "  Total iconic word occurrences: "
            f"{total_iconic_occurrences_adults}"
        )
        print(
            "  Total non-iconic word occurrences: "
            f"{total_non_iconic_occurrences_adults}"
        )
        print(
            "  Unique iconic words: "
            f"{len(stats['adults']['iconic_words'])}"
        )
        print(
            "  Unique non-iconic words: "
            f"{len(stats['adults']['non_iconic_words'])}"
        )

        print("\nChildren statistics:")
        print(f"  Total words: {stats['children']['total_words']}")

        total_iconic_occurrences_children = stats["children"][
            "total_iconic_occurrences"
        ]
        total_non_iconic_occurrences_children = stats["children"][
            "total_non_iconic_occurrences"
        ]

        print(
            "  Total iconic word occurrences: "
            f"{total_iconic_occurrences_children}"
        )
        print(
            "  Total non-iconic word occurrences: "
            f"{total_non_iconic_occurrences_children}"
        )
        print(
            "  Unique iconic words: "
            f"{len(stats['children']['iconic_words'])}"
        )
        print(
            "  Unique non-iconic words: "
            f"{len(stats['children']['non_iconic_words'])}"
        )

        print("\nTop 10 iconic words used by adults:")
        adult_iconic = sorted(
            stats["adults"]["iconic_words"].items(),
            key=lambda x: x[1]["count"],
            reverse=True,
        )[:10]
        total_top10_adult_iconic = sum(data["count"] for _, data in adult_iconic)
        percentage_top10_adult_iconic = (
            total_top10_adult_iconic / total_iconic_occurrences_adults * 100
            if total_iconic_occurrences_adults > 0
            else 0
        )
        for word, data in adult_iconic:
            print(f"  {word}: {data['count']} uses, rating: {data['rating']}")
        print(
            "  Top 10 iconic word usage percentage: "
            f"{percentage_top10_adult_iconic:.1f}% of total iconic words"
        )

        print("\nTop 10 iconic words used by children:")
        child_iconic = sorted(
            stats["children"]["iconic_words"].items(),
            key=lambda x: x[1]["count"],
            reverse=True,
        )[:10]
        total_top10_child_iconic = sum(data["count"] for _, data in child_iconic)
        percentage_top10_child_iconic = (
            total_top10_child_iconic / total_iconic_occurrences_children * 100
            if total_iconic_occurrences_children > 0
            else 0
        )
        for word, data in child_iconic:
            print(f"  {word}: {data['count']} uses, rating: {data['rating']}")
        print(
            "  Top 10 iconic word usage percentage: "
            f"{percentage_top10_child_iconic:.1f}% of total iconic words"
        )
        print("-" * 50)

        print("\nTop 10 non-iconic words used by children:")
        child_non_iconic = sorted(
            stats["children"]["non_iconic_words"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10]
        total_top10_child_non_iconic = sum(count for _, count in child_non_iconic)
        percentage_top10_child_non_iconic = (
            total_top10_child_non_iconic / total_non_iconic_occurrences_children * 100
            if total_non_iconic_occurrences_children > 0
            else 0
        )
        for word, count in child_non_iconic:
            print(f"  {word}: {count} uses")
        print(
            "  Top 10 non-iconic word usage percentage: "
            f"{percentage_top10_child_non_iconic:.1f}% of total non-iconic words"
        )
        print("-" * 50)

        print("\nTop 10 non-iconic words used by adults:")
        adult_non_iconic = sorted(
            stats["adults"]["non_iconic_words"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10]
        total_top10_adult_non_iconic = sum(count for _, count in adult_non_iconic)
        percentage_top10_adult_non_iconic = (
            total_top10_adult_non_iconic / total_non_iconic_occurrences_adults * 100
            if total_non_iconic_occurrences_adults > 0
            else 0
        )
        for word, count in adult_non_iconic:
            print(f"  {word}: {count} uses")
        print(
            "  Top 10 non-iconic word usage percentage: "
            f"{percentage_top10_adult_non_iconic:.1f}% of total non-iconic words"
        )
        print("-" * 50)
