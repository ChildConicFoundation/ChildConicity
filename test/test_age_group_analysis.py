from src.analysis.age_group_analysis import (
    create_age_group_statistics,
    print_age_group_statistics,
    print_valid_words_statistics,
    process_valid_words_by_age_group,
)
from src.analysis.grammatical_type_analysis import (
    TYPE_COUNT_ONLY_ONCE,
    collect_grouped_grammatical_categories,
    create_grammatical_type_stats,
    create_grammatical_type_stats_by_category,
)


class FakeIconicityModel:
    def __init__(self, words):
        self.words = words

    def get_all_word_data(self):
        return self.words


def test_create_age_group_statistics_counts_children_and_adults():
    grouped_data = {
        "01Y01Q": {
            "children_data": {
                "1": {"text": "ball ball mama"},
            },
            "adults_data": {
                "1": {"text": "look ball"},
            },
        }
    }
    model = FakeIconicityModel({"ball": {"rating": 3.3}, "look": {"rating": 5.6}})

    stats = create_age_group_statistics(grouped_data, model)

    assert stats["01Y01Q"]["children_counted_words"]["ball"]["count"] == 2
    assert stats["01Y01Q"]["children_counted_words"]["mama"]["count"] == 1
    assert stats["01Y01Q"]["adults_counted_words"]["look"]["count"] == 1
    assert stats["01Y01Q"]["all_iconicity_words"]["ball"]["rating"] == 3.3


def test_process_valid_words_by_age_group_splits_iconic_and_non_iconic():
    age_group_stats = {
        "01Y01Q": {
            "children_counted_words": {
                "ball": {"count": 2},
                "xxx": {"count": 1},
            },
            "adults_counted_words": {
                "look": {"count": 3},
                "yeah": {"count": 2},
            },
        }
    }
    model = FakeIconicityModel({"ball": {"rating": 3.3}, "look": {"rating": 5.6}})

    valid_stats = process_valid_words_by_age_group(age_group_stats, model)

    assert valid_stats["01Y01Q"]["children"]["iconic_words"]["ball"]["count"] == 2
    assert valid_stats["01Y01Q"]["children"]["non_iconic_words"]["xxx"] == 1
    assert valid_stats["01Y01Q"]["adults"]["iconic_words"]["look"]["rating"] == 5.6
    assert valid_stats["01Y01Q"]["adults"]["non_iconic_words"]["yeah"] == 2


def test_create_grammatical_type_stats_adapts_grouped_mor_lemmas_for_plotter():
    grouped_data = {
        "01Y01Q": {
            "children_data": {
                "1": {"category": "noun", "lemma": "Ball"},
                "2": {"category": "noun", "lemma": "ball"},
                "3": {"category": "verb", "lemma": "look"},
                "4": {"category": "intj", "lemma": "zzz"},
            },
            "adults_data": {
                "1": {"category": "verb", "lemma": "Look"},
                "2": {"category": "noun", "lemma": "shoe"},
            },
        }
    }
    model = FakeIconicityModel(
        {
            "ball": {"rating": 3.3},
            "look": {"rating": 5.6},
            float("nan"): {"rating": 1.0},
        }
    )

    stats = create_grammatical_type_stats(grouped_data, model)

    assert stats["01Y01Q"]["children"]["total_words"] == 4
    assert stats["01Y01Q"]["children"]["iconic_words"]["ball"] == {
        "count": 2,
        "rating": 3.3,
    }
    assert stats["01Y01Q"]["children"]["iconic_words"]["look"]["count"] == 1
    assert stats["01Y01Q"]["children"]["non_iconic_words"]["zzz"] == 1
    assert stats["01Y01Q"]["adults"]["iconic_words"]["look"]["count"] == 1
    assert stats["01Y01Q"]["adults"]["non_iconic_words"]["shoe"] == 1


def test_create_grammatical_type_stats_can_ignore_repetition_counts():
    grouped_data = {
        "01Y01Q": {
            "children_data": {
                "1": {
                    "category": "noun",
                    "lemma": "ball",
                    "attributes": [],
                    "raw_token": "noun|ball",
                    "count": 7,
                },
                "2": {
                    "category": "verb",
                    "lemma": "look",
                    "attributes": ["Fin"],
                    "raw_token": "verb|look-Fin",
                    "count": 3,
                },
            },
            "adults_data": {},
        }
    }
    model = FakeIconicityModel(
        {
            "ball": {"rating": 3.3},
            "look": {"rating": 5.6},
        }
    )

    with_repetitions = create_grammatical_type_stats(grouped_data, model)
    only_once = create_grammatical_type_stats(
        grouped_data,
        model,
        count_mode=TYPE_COUNT_ONLY_ONCE,
    )

    assert with_repetitions["01Y01Q"]["children"]["total_words"] == 10
    assert with_repetitions["01Y01Q"]["children"]["iconic_words"]["ball"]["count"] == 7
    assert only_once["01Y01Q"]["children"]["total_words"] == 2
    assert only_once["01Y01Q"]["children"]["iconic_words"]["ball"]["count"] == 1
    assert only_once["01Y01Q"]["children"]["iconic_words"]["look"]["count"] == 1


def test_create_grammatical_type_stats_by_category_keeps_category_cuts_separate():
    grouped_data = {
        "01Y01Q": {
            "children_data": {
                "1": {"category": "noun", "lemma": "ball"},
                "2": {"category": "verb", "lemma": "ball"},
            },
            "adults_data": {},
        }
    }
    model = FakeIconicityModel({"ball": {"rating": 3.3}})

    by_category = create_grammatical_type_stats_by_category(grouped_data, model)

    assert collect_grouped_grammatical_categories(grouped_data) == ["noun", "verb"]
    assert by_category["noun"]["01Y01Q"]["children"]["total_words"] == 1
    assert by_category["verb"]["01Y01Q"]["children"]["total_words"] == 1
    assert by_category["noun"]["01Y01Q"]["children"]["iconic_words"]["ball"]["count"] == 1
    assert by_category["verb"]["01Y01Q"]["children"]["iconic_words"]["ball"]["count"] == 1


def test_create_grammatical_type_stats_by_category_can_ignore_repetition_counts():
    grouped_data = {
        "01Y01Q": {
            "children_data": {
                "1": {"category": "noun", "lemma": "ball", "count": 5},
                "2": {"category": "verb", "lemma": "ball", "count": 2},
            },
            "adults_data": {},
        }
    }
    model = FakeIconicityModel({"ball": {"rating": 3.3}})

    by_category = create_grammatical_type_stats_by_category(
        grouped_data,
        model,
        count_mode=TYPE_COUNT_ONLY_ONCE,
    )

    assert by_category["noun"]["01Y01Q"]["children"]["total_words"] == 1
    assert by_category["verb"]["01Y01Q"]["children"]["total_words"] == 1
    assert by_category["noun"]["01Y01Q"]["children"]["iconic_words"]["ball"]["count"] == 1
    assert by_category["verb"]["01Y01Q"]["children"]["iconic_words"]["ball"]["count"] == 1


def test_print_functions_emit_summary(capsys):
    age_group_stats = {
        "01Y01Q": {
            "children_counted_words": {"ball": {"count": 2}},
            "adults_counted_words": {"look": {"count": 1}},
            "all_iconicity_words": {"ball": {"rating": 3.3}, "look": {"rating": 5.6}},
        }
    }
    valid_words_stats = {
        "01Y01Q": {
            "adults": {
                "total_words": 3,
                "iconic_words": {"look": {"count": 1, "rating": 5.6}},
                "non_iconic_words": {"yeah": 2},
                "total_iconic_occurrences": 1,
                "total_non_iconic_occurrences": 2,
                "unique_iconic_words": {"look"},
                "unique_non_iconic_words": {"yeah"},
            },
            "children": {
                "total_words": 2,
                "iconic_words": {"ball": {"count": 2, "rating": 3.3}},
                "non_iconic_words": {},
                "total_iconic_occurrences": 2,
                "total_non_iconic_occurrences": 0,
                "unique_iconic_words": {"ball"},
                "unique_non_iconic_words": set(),
            },
        }
    }

    print_age_group_statistics(age_group_stats)
    print_valid_words_statistics(valid_words_stats)
    captured = capsys.readouterr().out

    assert "Grupo de edad 01Y01Q" in captured
    assert "Top palabras de niños" in captured
    assert "Top 10 palabras icónicas más usadas por adultos" in captured
    assert "Porcentaje de uso de las top 10 palabras icónicas" in captured
