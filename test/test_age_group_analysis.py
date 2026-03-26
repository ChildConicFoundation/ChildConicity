from src.analysis.age_group_analysis import (
    create_age_group_statistics,
    print_age_group_statistics,
    print_valid_words_statistics,
    process_valid_words_by_age_group,
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
