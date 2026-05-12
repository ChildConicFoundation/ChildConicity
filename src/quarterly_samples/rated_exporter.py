import csv
import json
from collections import defaultdict
from pathlib import Path


def load_iconicity_ratings(csv_path):
    ratings = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            word = row["word"].lower().strip()
            ratings[word] = {
                "iconicity_rating": float(row["rating"]),
                "iconicity_sd": float(row["rating_sd"]),
                "iconicity_prop_known": float(row["prop_known"]),
                "iconicity_n_ratings": int(row["n_ratings"]),
            }
    return ratings


def _iconicity_fields(lemma, ratings):
    data = ratings.get(lemma.lower().strip())
    if data:
        return data
    return {
        "iconicity_rating": None,
        "iconicity_sd": None,
        "iconicity_prop_known": None,
        "iconicity_n_ratings": None,
    }


def _enrich_entry(entry, ratings):
    return {**entry, **_iconicity_fields(entry.get("lemma", ""), ratings)}


def _merge_to_lema(entries, ratings):
    by_lemma = defaultdict(list)
    for entry in entries:
        by_lemma[entry["lemma"]].append(entry)

    merged = []
    for lemma, group in sorted(by_lemma.items()):
        categories = sorted(set(e["category"] for e in group))
        attributes = sorted(set(a for e in group for a in e.get("attributes", [])))

        counts_by_child = defaultdict(int)
        for e in group:
            for child, c in e.get("counts_by_child", {}).items():
                counts_by_child[child] += c

        first = group[0]
        entry = {
            "quarter": first["quarter"],
            "speaker_group": first["speaker_group"],
            "lemma": lemma,
            "category": "|".join(categories),
            "attributes": attributes,
            "count": sum(e["count"] for e in group),
            "counts_by_child": dict(counts_by_child),
        }
        merged.append(_enrich_entry(entry, ratings))

    for i, e in enumerate(merged, 1):
        e["id"] = i

    return merged


_WC_FIELDS = [
    "quarter", "speaker_group", "id", "category", "lemma", "attributes",
    "raw_token", "count", "counts_by_child",
    "iconicity_rating", "iconicity_sd", "iconicity_prop_known", "iconicity_n_ratings",
]

_LC_FIELDS = [
    "quarter", "speaker_group", "id", "lemma", "category", "attributes",
    "count", "counts_by_child",
    "iconicity_rating", "iconicity_sd", "iconicity_prop_known", "iconicity_n_ratings",
]


def _to_csv_row(entry, fieldnames):
    row = {}
    for field in fieldnames:
        value = entry.get(field, "")
        if field == "attributes":
            value = "|".join(value) if value else ""
        elif isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        elif value is None:
            value = ""
        row[field] = value
    return row


def _write_csv(path, entries, fieldnames):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(_to_csv_row(e, fieldnames) for e in entries)


def enrich_word_count(source, ratings):
    return {
        **source,
        "lemma_entries": [_enrich_entry(e, ratings) for e in source.get("lemma_entries", [])],
    }


def build_lema_count(source, ratings):
    merged = _merge_to_lema(source.get("lemma_entries", []), ratings)
    return {
        "quarter": source["quarter"],
        "speaker_group": source["speaker_group"],
        "total_lemma_entries": len(merged),
        "total_occurrences": sum(e["count"] for e in merged),
        "lemma_entries": merged,
    }


def export_rated(
    source_root,
    output_root,
    iconicity_csv,
    groups=("adults", "children", "other_children"),
):
    ratings = load_iconicity_ratings(iconicity_csv)
    source_root = Path(source_root)
    output_root = Path(output_root)

    for group in groups:
        word_count_dir = source_root / group / "WordCount"
        if not word_count_dir.exists():
            continue

        out_wc_dir = output_root / group / "WordCount"
        out_lc_dir = output_root / group / "LemaCount"
        out_wc_dir.mkdir(parents=True, exist_ok=True)
        out_lc_dir.mkdir(parents=True, exist_ok=True)

        files = sorted(word_count_dir.glob("*.json"))
        for json_path in files:
            with open(json_path, encoding="utf-8") as f:
                source = json.load(f)

            wc = enrich_word_count(source, ratings)
            lc = build_lema_count(source, ratings)

            stem = json_path.stem

            with open(out_wc_dir / f"{stem}.json", "w", encoding="utf-8") as f:
                json.dump(wc, f, ensure_ascii=False, indent=2)
            _write_csv(out_wc_dir / f"{stem}.csv", wc["lemma_entries"], _WC_FIELDS)

            with open(out_lc_dir / f"{stem}.json", "w", encoding="utf-8") as f:
                json.dump(lc, f, ensure_ascii=False, indent=2)
            _write_csv(out_lc_dir / f"{stem}.csv", lc["lemma_entries"], _LC_FIELDS)

        print(f"[{group}] {len(files)} trimestres procesados")
