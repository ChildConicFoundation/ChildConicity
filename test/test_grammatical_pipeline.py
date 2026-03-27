import csv
import json
from pathlib import Path

from src.data_io.grammatical_formatter import GrammaticalDataFormatter
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
