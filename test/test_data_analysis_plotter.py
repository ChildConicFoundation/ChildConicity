from src.visualization.data_analysis_plotter import DataAnalysisPlotter


def _empty_group_stats():
    return {
        "total_words": 0,
        "iconic_words": {},
        "non_iconic_words": {},
        "total_iconic_occurrences": 0,
        "total_non_iconic_occurrences": 0,
        "unique_iconic_words": set(),
        "unique_non_iconic_words": set(),
    }


def _group_stats(words):
    group_stats = _empty_group_stats()

    for word, rating in words.items():
        group_stats["total_words"] += 1
        group_stats["total_iconic_occurrences"] += 1
        group_stats["unique_iconic_words"].add(word)
        group_stats["iconic_words"][word] = {
            "count": 1,
            "rating": rating,
        }

    return group_stats


def test_type_distribution_series_use_total_scope_denominator():
    stats_by_scope = {
        "total": {
            "02Y02Q": {
                "children": _group_stats(
                    {
                        "ball": 3.0,
                        "car": 4.0,
                        "look": 5.0,
                    }
                ),
                "adults": _empty_group_stats(),
            }
        },
        "noun": {
            "02Y02Q": {
                "children": _group_stats(
                    {
                        "ball": 3.0,
                        "car": 4.0,
                    }
                ),
                "adults": _empty_group_stats(),
            }
        },
    }

    series = DataAnalysisPlotter(
        stats_by_scope["total"]
    )._build_iconicity_distribution_series_for_age_group(
        stats_by_scope,
        "02Y02Q",
    )

    noun_series = next(serie for serie in series if serie["label"] == "Niños - noun")
    total_series = next(serie for serie in series if serie["label"] == "Niños - total")

    assert total_series["total_words"] == 3
    assert total_series["denominator"] == 3
    assert noun_series["total_words"] == 2
    assert noun_series["denominator"] == 3


def test_type_distribution_series_can_be_limited_to_adults():
    stats_by_scope = {
        "total": {
            "02Y02Q": {
                "children": _group_stats({"ball": 3.0}),
                "adults": _group_stats({"look": 5.0}),
            }
        }
    }

    series = DataAnalysisPlotter(
        stats_by_scope["total"]
    )._build_iconicity_distribution_series_for_age_group(
        stats_by_scope,
        "02Y02Q",
        speaker_groups_to_plot=("adults",),
    )

    assert [serie["label"] for serie in series] == ["Adultos - total"]


def test_calculate_cumulative_counts_keeps_intermediate_bins():
    plotter = DataAnalysisPlotter({})
    x_axis = [3.0, 3.25, 3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0]

    cumulative = plotter._calculate_cumulative_counts(
        [(3.0, 1), (5.0, 1)],
        x_axis,
    )

    assert cumulative.tolist() == [1, 1, 1, 1, 1, 1, 1, 1, 2]
