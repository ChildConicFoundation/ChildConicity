import csv
import json
from pathlib import Path

from src.quarterly_samples import (
    QuarterlySampleExporter,
    QuarterlySampleTransformer,
    ValidWordsStatsExporter,
    get_age_quarter,
    group_data_by_age,
)


def test_get_age_quarter_from_verbose_age():
    assert get_age_quarter("1 years 06 months 26 days") == "01Y02Q"


def test_get_age_quarter_from_compact_age():
    assert get_age_quarter("020508") == "02Y02Q"


def test_group_data_by_age_groups_children_and_adults():
    processed_data = {
        "Corpus_modified": {
            "Post": {
                "Lew": {
                    "files": [
                        {
                            "metadata": {
                                "file_path": "Corpus_modified/Post/Lew/020508.cha",
                                "child_age": "2 years 05 months 08 days",
                                "child_name": "Lew",
                            },
                            "children_data": {
                                1: {"text": "more juice", "speaker": "CHI", "timestamp": None},
                            },
                            "other_children_data": {
                                1: {"text": "mine too", "speaker": "JEN", "timestamp": None},
                            },
                            "adults_data": {
                                1: {"text": "do you want more", "speaker": "MOT", "timestamp": None},
                            },
                        }
                    ]
                }
            }
        }
    }

    grouped_data = group_data_by_age(processed_data)

    assert "02Y02Q" in grouped_data
    assert grouped_data["02Y02Q"]["children_data"]["1"]["text"] == "more juice"
    assert grouped_data["02Y02Q"]["other_children_data"]["1"]["text"] == "mine too"
    assert grouped_data["02Y02Q"]["adults_data"]["1"]["text"] == "do you want more"


def test_quarterly_sample_exporter_creates_quarter_files(tmp_path):
    grouped_data = {
        "02Y02Q": {
            "children_data": {
                "1": {"text": "more juice"},
                "2": {"text": "want cookie"},
            },
            "other_children_data": {
                "1": {"text": "me too"},
            },
            "adults_data": {
                "1": {"text": "do you want more"},
            },
            "files": [],
        }
    }

    exporter = QuarterlySampleExporter(output_dir=str(tmp_path / "quarterly_samples"))
    exported_files = exporter.export(grouped_data)

    adults_path = Path(exported_files["adults"]["02Y02Q"])
    children_path = Path(exported_files["children"]["02Y02Q"])
    other_children_path = Path(exported_files["other_children"]["02Y02Q"])

    assert adults_path.exists()
    assert children_path.exists()
    assert other_children_path.exists()
    assert adults_path.read_text(encoding="utf-8") == "do you want more\n"
    assert children_path.read_text(encoding="utf-8") == "more juice\nwant cookie\n"
    assert other_children_path.read_text(encoding="utf-8") == "me too\n"


def test_quarterly_sample_transformer_creates_json_and_csv(tmp_path):
    grouped_data = {
        "02Y02Q": {
            "children_data": {
                "1": {"text": "more juice"},
                "2": {"text": "want cookie"},
            },
            "other_children_data": {
                "1": {"text": "me too"},
            },
            "adults_data": {
                "1": {"text": "do you want more"},
            },
            "files": [],
        }
    }

    base_dir = tmp_path / "quarterly_samples"
    exporter = QuarterlySampleExporter(output_dir=str(base_dir))
    exporter.export(grouped_data)

    transformer = QuarterlySampleTransformer(base_dir=str(base_dir))
    outputs = transformer.transform()

    children_json_path = Path(outputs["children"]["02Y02Q"]["json"])
    children_csv_path = Path(outputs["children"]["02Y02Q"]["csv"])

    assert children_json_path.exists()
    assert children_csv_path.exists()

    with open(children_json_path, "r", encoding="utf-8") as file:
        json_payload = json.load(file)

    assert json_payload["quarter"] == "02Y02Q"
    assert json_payload["speaker_group"] == "children"
    assert json_payload["total_rows"] == 2
    assert json_payload["rows"][0]["text"] == "more juice"

    with open(children_csv_path, "r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["quarter"] == "02Y02Q"
    assert rows[0]["speaker_group"] == "children"
    assert rows[0]["line_number"] == "1"
    assert rows[0]["text"] == "more juice"


def test_valid_words_stats_exporter_creates_plotter_aligned_exports(tmp_path):
    valid_words_stats = {
        "02Y02Q": {
            "adults": {
                "total_words": 10,
                "iconic_words": {
                    "go": {"count": 4, "rating": 4.9},
                },
                "non_iconic_words": {
                    "yeah": 2,
                },
                "total_iconic_occurrences": 4,
                "total_non_iconic_occurrences": 2,
                "unique_iconic_words": {"go"},
                "unique_non_iconic_words": {"yeah"},
            },
            "children": {
                "total_words": 8,
                "iconic_words": {
                    "ball": {"count": 3, "rating": 3.3},
                },
                "non_iconic_words": {
                    "xxx": 1,
                },
                "total_iconic_occurrences": 3,
                "total_non_iconic_occurrences": 1,
                "unique_iconic_words": {"ball"},
                "unique_non_iconic_words": {"xxx"},
            },
        }
    }

    exporter = ValidWordsStatsExporter(output_dir=str(tmp_path / "quarterly_valid_words"))
    outputs = exporter.export(valid_words_stats)

    adults_json_path = Path(outputs["adults"]["02Y02Q"]["json"])
    adults_csv_path = Path(outputs["adults"]["02Y02Q"]["csv"])
    adults_summary_path = Path(outputs["adults"]["summary"])

    assert adults_json_path.exists()
    assert adults_csv_path.exists()
    assert adults_summary_path.exists()

    with open(adults_json_path, "r", encoding="utf-8") as file:
        payload = json.load(file)

    assert payload["quarter"] == "02Y02Q"
    assert payload["speaker_group"] == "adults"
    assert payload["total_rows"] == 2
    assert payload["summary"]["total_words"] == 10
    assert payload["summary"]["iconic_percentage"] == 40.0
    assert payload["rows"][0]["id"] == 1
    assert payload["rows"][0]["word"] == "go"
    assert payload["rows"][1]["id"] == 2
    assert payload["rows"][1]["word"] == "yeah"

    with open(adults_csv_path, "r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["quarter"] == "02Y02Q"
    assert rows[0]["speaker_group"] == "adults"
    assert rows[0]["id"] == "1"
    assert rows[0]["word"] == "go"
    assert rows[0]["is_iconic"] == "True"
    assert rows[0]["rating"] == "4.9"
    assert rows[1]["id"] == "2"
    assert rows[1]["word"] == "yeah"

    with open(adults_summary_path, "r", encoding="utf-8", newline="") as file:
        summary_rows = list(csv.DictReader(file))

    assert len(summary_rows) == 1
    assert summary_rows[0]["quarter"] == "02Y02Q"
    assert summary_rows[0]["total_words"] == "10"
