import csv
import json
from pathlib import Path

from src.data_io.grammatical_formatter import GrammaticalDataFormatter
from src.data_io.grammatical_corpus_processing import (
    collect_grammatical_categories,
    process_grammatical_data_with_formatter,
    run_grammatical_pipeline,
)
from src.data_io.reader import Reader
from src.quarterly_samples import GrammaticalCategoriesExporter, group_data_by_age


def test_reader_extracts_morphological_utterances():
    content = """
*MOT:\tpull it up yoursel(f) ! \x15131_1537\x15
%mor:\tverb|pull-Fin-Imp-S pron|it-Prs-Acc-S3 adp|up pron|yourself-Prs-Acc-S2 !
*CHI:\t&=vocalize . \x1515320_16139\x15
*MOT:\they I'll point at you too . \x1513333_14830\x15
%mor:\tintj|hey pron|I-Prs-Nom-S1~aux|will-Fin-S verb|point-Inf-S adp|at pron|you-Prs-Acc-S2 adv|too .
""".strip()

    reader = Reader()
    utterances = reader._extract_morphological_utterances(content)

    assert len(utterances) == 2
    assert utterances[0]["speaker"] == "MOT"
    assert utterances[0]["tokens"][0]["category"] == "verb"
    assert utterances[0]["tokens"][0]["lemma"] == "pull"
    assert utterances[0]["tokens"][0]["attributes"] == ["Fin", "Imp", "S"]
    assert utterances[1]["tokens"][2]["category"] == "aux"
    assert utterances[1]["tokens"][2]["lemma"] == "will"


def test_grammatical_formatter_splits_children_and_adults(tmp_path):
    file_path = tmp_path / "sample.cha"
    file_path.write_text(
        """
@UTF8
@Languages:\teng
@ChildAge: 1 years 06 months 00 days
@ChildName: Kid
*MOT:\tpull it up ! \x15131_1537\x15
%mor:\tverb|pull-Fin-Imp-S pron|it-Prs-Acc-S3 adp|up !
*CHI:\tball . \x15131_1537\x15
%mor:\tnoun|ball .
""".strip(),
        encoding="utf-8",
    )

    formatter = GrammaticalDataFormatter()
    children_data, adults_data = formatter.format_cha_data_from(str(file_path))

    assert children_data[1]["category"] == "noun"
    assert children_data[1]["lemma"] == "ball"
    assert adults_data[1]["category"] == "verb"
    assert adults_data[1]["lemma"] == "pull"
    assert adults_data[2]["lemma"] == "it"


def test_grammatical_formatter_filters_selected_categories(tmp_path):
    file_path = tmp_path / "sample_filtered.cha"
    file_path.write_text(
        """
@UTF8
@Languages:\teng
@ChildAge: 1 years 06 months 00 days
@ChildName: Kid
*MOT:\tpull ball up ! \x15131_1537\x15
%mor:\tverb|pull-Fin-Imp-S noun|ball adp|up !
*CHI:\tball up . \x15131_1537\x15
%mor:\tnoun|ball adp|up .
""".strip(),
        encoding="utf-8",
    )

    formatter = GrammaticalDataFormatter(grammatical_categories=["noun"])
    children_data, adults_data = formatter.format_cha_data_from(str(file_path))

    assert len(children_data) == 1
    assert children_data[1]["category"] == "noun"
    assert children_data[1]["lemma"] == "ball"
    assert len(adults_data) == 1
    assert adults_data[1]["category"] == "noun"
    assert adults_data[1]["lemma"] == "ball"


def test_collect_grammatical_categories_returns_sorted_categories():
    corpus_data = {
        "Corpus_modified": {
            "Post": {
                "Lew": {
                    "files": [
                        {
                            "metadata": {
                                "morphological_utterances": [
                                    {
                                        "tokens": [
                                            {"category": "verb"},
                                            {"category": "noun"},
                                        ]
                                    },
                                    {"tokens": [{"category": "adj"}]},
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }

    categories = collect_grammatical_categories(corpus_data)

    assert categories == ["adj", "noun", "verb"]


def test_process_grammatical_data_with_formatter_filters_categories(tmp_path):
    file_path = tmp_path / "sample_pipeline.cha"
    file_path.write_text(
        """
@UTF8
@Languages:\teng
@ChildAge: 1 years 06 months 00 days
@ChildName: Kid
*MOT:\tpull ball up ! \x15131_1537\x15
%mor:\tverb|pull-Fin-Imp-S noun|ball adp|up !
*CHI:\tball up . \x15131_1537\x15
%mor:\tnoun|ball adp|up .
""".strip(),
        encoding="utf-8",
    )

    corpus_data = {
        "Corpus_modified": {
            "Post": {
                "Lew": {
                    "files": [
                        {
                            "metadata": {
                                "file_path": str(file_path),
                                "child_age": "1 years 06 months 00 days",
                                "child_name": "Kid",
                            }
                        }
                    ]
                }
            }
        }
    }

    processed_data = process_grammatical_data_with_formatter(
        corpus_data, grammatical_categories=["noun"]
    )
    processed_file = processed_data["Corpus_modified"]["Post"]["Lew"]["files"][0]

    assert len(processed_file["children_data"]) == 1
    assert processed_file["children_data"][1]["category"] == "noun"
    assert processed_file["children_data"][1]["lemma"] == "ball"
    assert len(processed_file["adults_data"]) == 1
    assert processed_file["adults_data"][1]["category"] == "noun"
    assert processed_file["adults_data"][1]["lemma"] == "ball"


def test_run_grammatical_pipeline_exports_filtered_data(tmp_path):
    file_path = tmp_path / "sample_run_pipeline.cha"
    file_path.write_text(
        """
@UTF8
@Languages:\teng
@ChildAge: 1 years 06 months 00 days
@ChildName: Kid
*MOT:\tpull ball up ! \x15131_1537\x15
%mor:\tverb|pull-Fin-Imp-S noun|ball adp|up !
*CHI:\tball up . \x15131_1537\x15
%mor:\tnoun|ball adp|up .
""".strip(),
        encoding="utf-8",
    )

    corpus_data = {
        "Corpus_modified": {
            "Post": {
                "Lew": {
                    "files": [
                        {
                            "metadata": {
                                "file_path": str(file_path),
                                "child_age": "1 years 06 months 00 days",
                                "child_name": "Kid",
                            }
                        }
                    ]
                }
            }
        }
    }

    result = run_grammatical_pipeline(
        corpus_data,
        output_dir=str(tmp_path / "quarterly_grammatical_categories"),
        grammatical_categories=["noun"],
    )

    processed_file = result["processed_data"]["Corpus_modified"]["Post"]["Lew"]["files"][0]
    assert len(processed_file["children_data"]) == 1
    assert len(processed_file["adults_data"]) == 1
    assert "01Y02Q" in result["grouped_data"]
    assert "Raw" in result["outputs"]["children"]


def test_grammatical_exporter_exports_grouped_rows(tmp_path):
    processed_data = {
        "Corpus_modified": {
            "Post": {
                "Lew": {
                    "files": [
                        {
                            "metadata": {
                                "file_path": "Corpus_modified/Post/Lew/a.cha",
                                "child_age": "1 years 06 months 00 days",
                                "child_name": "Lew",
                            },
                            "children_data": {
                                "1": {
                                    "category": "noun",
                                    "lemma": "ball",
                                    "attributes": [],
                                    "raw_token": "noun|ball",
                                }
                            },
                            "adults_data": {
                                "1": {
                                    "category": "verb",
                                    "lemma": "pull",
                                    "attributes": ["Fin", "Imp", "S"],
                                    "raw_token": "verb|pull-Fin-Imp-S",
                                },
                                "2": {
                                    "category": "verb",
                                    "lemma": "pull",
                                    "attributes": ["Fin", "Imp", "S"],
                                    "raw_token": "verb|pull-Fin-Imp-S",
                                }
                            },
                        }
                    ]
                }
            }
        }
    }

    grouped = group_data_by_age(processed_data)
    outputs = GrammaticalCategoriesExporter(
        output_dir=str(tmp_path / "quarterly_grammatical_categories")
    ).export(grouped)

    adults_json = Path(outputs["adults"]["Raw"]["01Y02Q"]["json"])
    adults_csv = Path(outputs["adults"]["Raw"]["01Y02Q"]["csv"])
    raw_summary_csv = Path(outputs["adults"]["Raw"]["summary"])
    word_count_json = Path(outputs["adults"]["WordCount"]["01Y02Q"]["json"])
    word_count_csv = Path(outputs["adults"]["WordCount"]["01Y02Q"]["csv"])
    word_count_summary_csv = Path(outputs["adults"]["WordCount"]["summary"])

    payload = json.loads(adults_json.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(adults_csv.open(encoding="utf-8")))
    raw_summary = list(csv.DictReader(raw_summary_csv.open(encoding="utf-8")))
    word_count_payload = json.loads(word_count_json.read_text(encoding="utf-8"))
    word_count_rows = list(csv.DictReader(word_count_csv.open(encoding="utf-8")))
    word_count_summary = list(
        csv.DictReader(word_count_summary_csv.open(encoding="utf-8"))
    )

    assert payload["total_rows"] == 2
    assert payload["rows"][0]["id"] == 1
    assert payload["rows"][0]["category"] == "verb"
    assert payload["rows"][0]["lemma"] == "pull"
    assert payload["rows"][0]["attributes"] == ["Fin", "Imp", "S"]
    assert rows[0]["id"] == "1"
    assert rows[0]["raw_token"] == "verb|pull-Fin-Imp-S"
    assert rows[0]["attributes"] == "Fin|Imp|S"
    assert raw_summary[0]["quarter"] == "01Y02Q"
    assert word_count_payload["total_lemma_entries"] == 1
    assert word_count_payload["total_occurrences"] == 2
    assert word_count_payload["lemma_entries"][0]["id"] == 1
    assert word_count_payload["lemma_entries"][0]["count"] == 2
    assert word_count_rows[0]["id"] == "1"
    assert word_count_rows[0]["count"] == "2"
    assert word_count_rows[0]["attributes"] == "Fin|Imp|S"
    assert word_count_summary[0]["unique_lemma_entries"] == "1"
    assert word_count_summary[0]["total_occurrences"] == "2"
