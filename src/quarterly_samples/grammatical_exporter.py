import csv
import json
from pathlib import Path
from collections import Counter


class GrammaticalCategoriesExporter:
    """
    Exporta las categorías gramaticales agrupadas por quarter sin aplicar filtrado.
    """

    def __init__(self, output_dir="quarterly_grammatical_categories"):
        self.output_dir = Path(output_dir)

    def export(self, grouped_data):
        outputs = {
            "adults": {"Raw": {}, "WordCount": {}},
            "children": {"Raw": {}, "WordCount": {}},
            "other_children": {"Raw": {}, "WordCount": {}},
        }

        for speaker_group in ("adults", "children", "other_children"):
            group_dir = self.output_dir / speaker_group
            group_dir.mkdir(parents=True, exist_ok=True)
            self._clear_previous_exports(group_dir)
            raw_dir = group_dir / "Raw"
            word_count_dir = group_dir / "WordCount"
            raw_dir.mkdir(parents=True, exist_ok=True)
            word_count_dir.mkdir(parents=True, exist_ok=True)
            raw_summary_rows = []
            word_count_summary_rows = []

            for quarter, quarter_data in sorted(grouped_data.items()):
                data_key = f"{speaker_group}_data"
                rows = self._build_rows(
                    quarter,
                    speaker_group,
                    quarter_data.get(data_key, {}),
                )
                payload = {
                    "quarter": quarter,
                    "speaker_group": speaker_group,
                    "total_rows": len(rows),
                    "rows": rows,
                }

                json_path = raw_dir / f"{quarter}.json"
                csv_path = raw_dir / f"{quarter}.csv"
                self._write_json(json_path, payload)
                self._write_csv(csv_path, self._build_csv_rows(rows))

                outputs[speaker_group]["Raw"][quarter] = {
                    "json": str(json_path),
                    "csv": str(csv_path),
                }
                raw_summary_rows.append(
                    {
                        "quarter": quarter,
                        "speaker_group": speaker_group,
                        "total_rows": len(rows),
                    }
                )

                word_count_payload = self.build_word_count_payload_from_json(json_path)
                word_count_json_path = word_count_dir / f"{quarter}.json"
                word_count_csv_path = word_count_dir / f"{quarter}.csv"
                self._write_json(word_count_json_path, word_count_payload)
                self._write_word_count_csv(
                    word_count_csv_path, word_count_payload["lemma_entries"]
                )

                outputs[speaker_group]["WordCount"][quarter] = {
                    "json": str(word_count_json_path),
                    "csv": str(word_count_csv_path),
                }
                word_count_summary_rows.append(
                    {
                        "quarter": quarter,
                        "speaker_group": speaker_group,
                        "unique_lemma_entries": word_count_payload[
                            "total_lemma_entries"
                        ],
                        "total_occurrences": word_count_payload["total_occurrences"],
                    }
                )

            raw_summary_path = raw_dir / "summary.csv"
            self._write_summary_csv(raw_summary_path, raw_summary_rows)
            outputs[speaker_group]["Raw"]["summary"] = str(raw_summary_path)

            word_count_summary_path = word_count_dir / "summary.csv"
            self._write_word_count_summary_csv(
                word_count_summary_path, word_count_summary_rows
            )
            outputs[speaker_group]["WordCount"]["summary"] = str(
                word_count_summary_path
            )

        return outputs

    def _build_rows(self, quarter, speaker_group, entries):
        rows = []
        for index, entry in enumerate(entries.values(), start=1):
            rows.append(
                {
                    "quarter": quarter,
                    "speaker_group": speaker_group,
                    "id": index,
                    "category": entry.get("category", ""),
                    "lemma": entry.get("lemma", ""),
                    "attributes": entry.get("attributes", []),
                    "raw_token": entry.get("raw_token", ""),
                }
            )
        return rows

    def _build_csv_rows(self, rows):
        csv_rows = []
        for row in rows:
            csv_row = row.copy()
            csv_row["attributes"] = "|".join(row.get("attributes", []))
            csv_rows.append(csv_row)
        return csv_rows

    def build_word_count_payload_from_json(self, json_path):
        with open(json_path, "r", encoding="utf-8") as file:
            payload = json.load(file)

        counter = Counter()
        for row in payload.get("rows", []):
            attributes = tuple(row.get("attributes", []))
            counter[
                (
                    row.get("category", ""),
                    row.get("lemma", ""),
                    attributes,
                    row.get("raw_token", ""),
                )
            ] += 1

        counted_rows = []
        for index, ((category, lemma, attributes, raw_token), count) in enumerate(
            sorted(counter.items(), key=lambda item: (-item[1], item[0][0], item[0][1])),
            start=1,
        ):
            counted_rows.append(
                {
                    "quarter": payload.get("quarter", ""),
                    "speaker_group": payload.get("speaker_group", ""),
                    "id": index,
                    "category": category,
                    "lemma": lemma,
                    "attributes": list(attributes),
                    "raw_token": raw_token,
                    "count": count,
                }
            )

        return {
            "quarter": payload.get("quarter", ""),
            "speaker_group": payload.get("speaker_group", ""),
            "total_lemma_entries": len(counted_rows),
            "total_occurrences": sum(counter.values()),
            "lemma_entries": counted_rows,
        }

    def _write_json(self, file_path, payload):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def _write_csv(self, file_path, rows):
        fieldnames = [
            "quarter",
            "speaker_group",
            "id",
            "category",
            "lemma",
            "attributes",
            "raw_token",
        ]
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _write_summary_csv(self, file_path, rows):
        fieldnames = ["quarter", "speaker_group", "total_rows"]
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _write_word_count_csv(self, file_path, rows):
        fieldnames = [
            "quarter",
            "speaker_group",
            "id",
            "category",
            "lemma",
            "attributes",
            "raw_token",
            "count",
        ]
        csv_rows = self._build_csv_rows(rows)
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

    def _write_word_count_summary_csv(self, file_path, rows):
        fieldnames = [
            "quarter",
            "speaker_group",
            "unique_lemma_entries",
            "total_occurrences",
        ]
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _clear_previous_exports(self, group_dir):
        for child in group_dir.iterdir():
            if child.is_file() and child.suffix in {".csv", ".json"}:
                child.unlink()

        for subdir_name in ("Raw", "WordCount"):
            subdir = group_dir / subdir_name
            if not subdir.exists():
                continue

            for child in subdir.iterdir():
                if child.is_file() and child.suffix in {".csv", ".json"}:
                    child.unlink()
