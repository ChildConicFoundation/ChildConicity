import csv
import json

from src.quarterly_samples.rated_exporter import (
    build_lema_count,
    enrich_word_count,
    export_rated,
    load_iconicity_ratings,
)


def test_load_iconicity_ratings_reads_csv(tmp_path):
    csv_path = tmp_path / "ratings.csv"
    csv_path.write_text(
        "word,rating,rating_sd,prop_known,n_ratings\n"
        "Ball,3.3,0.5,0.9,10\n"
        "go,4.9,0.2,1.0,20\n",
        encoding="utf-8",
    )

    ratings = load_iconicity_ratings(csv_path)

    assert ratings["ball"]["iconicity_rating"] == 3.3
    assert ratings["go"]["iconicity_n_ratings"] == 20


def test_enrich_word_count_adds_iconicity_fields():
    source = {
        "quarter": "01Y01Q",
        "speaker_group": "children",
        "lemma_entries": [
            {"lemma": "Ball", "category": "noun", "count": 2},
            {"lemma": "zzz", "category": "intj", "count": 1},
        ],
    }
    ratings = {
        "ball": {
            "iconicity_rating": 3.3,
            "iconicity_sd": 0.5,
            "iconicity_prop_known": 0.9,
            "iconicity_n_ratings": 10,
        }
    }

    enriched = enrich_word_count(source, ratings)

    assert enriched["lemma_entries"][0]["iconicity_rating"] == 3.3
    assert enriched["lemma_entries"][1]["iconicity_rating"] is None


def test_build_lema_count_merges_duplicate_lemmas_and_enriches():
    source = {
        "quarter": "01Y01Q",
        "speaker_group": "children",
        "MLU_index": 1.5,
        "mlu_morpheme_count": 3,
        "mlu_utterance_count": 2,
        "lemma_entries": [
            {
                "lemma": "ball",
                "category": "noun",
                "attributes": [],
                "count": 2,
                "counts_by_child": {"Kid": 2},
            },
            {
                "lemma": "ball",
                "category": "noun",
                "attributes": ["Plur"],
                "count": 1,
                "counts_by_child": {"Kid": 1},
            },
        ],
    }
    ratings = {
        "ball": {
            "iconicity_rating": 3.3,
            "iconicity_sd": 0.5,
            "iconicity_prop_known": 0.9,
            "iconicity_n_ratings": 10,
        }
    }

    lema_count = build_lema_count(source, ratings)

    assert lema_count["total_lemma_entries"] == 1
    assert lema_count["total_occurrences"] == 3
    assert lema_count["lemma_entries"][0]["count"] == 3
    assert lema_count["lemma_entries"][0]["iconicity_rating"] == 3.3


def test_export_rated_writes_wordcount_and_lemacount(tmp_path):
    source_root = tmp_path / "source"
    word_count_dir = source_root / "children" / "WordCount"
    word_count_dir.mkdir(parents=True)
    payload = {
        "quarter": "01Y01Q",
        "speaker_group": "children",
        "total_lemma_entries": 1,
        "total_occurrences": 2,
        "MLU_index": 1.0,
        "mlu_morpheme_count": 2,
        "mlu_utterance_count": 2,
        "lemma_entries": [
            {
                "lemma": "ball",
                "category": "noun",
                "attributes": [],
                "raw_token": "noun|ball",
                "count": 2,
                "counts_by_child": {"Kid": 2},
            }
        ],
    }
    with open(word_count_dir / "01Y01Q.json", "w", encoding="utf-8") as file:
        json.dump(payload, file)

    ratings_csv = tmp_path / "ratings.csv"
    ratings_csv.write_text(
        "word,rating,rating_sd,prop_known,n_ratings\n"
        "ball,3.3,0.5,0.9,10\n",
        encoding="utf-8",
    )

    output_root = tmp_path / "rated"
    export_rated(source_root, output_root, ratings_csv, groups=("children",))

    wc_json = output_root / "children" / "WordCount" / "01Y01Q.json"
    lc_json = output_root / "children" / "LemaCount" / "01Y01Q.json"
    wc_csv = output_root / "children" / "WordCount" / "01Y01Q.csv"

    assert wc_json.exists()
    assert lc_json.exists()
    assert wc_csv.exists()

    with open(wc_json, encoding="utf-8") as file:
        enriched = json.load(file)

    assert enriched["lemma_entries"][0]["iconicity_rating"] == 3.3

    with open(wc_csv, encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["lemma"] == "ball"
    assert rows[0]["iconicity_rating"] == "3.3"
