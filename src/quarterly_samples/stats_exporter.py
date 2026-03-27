import csv
import json
from pathlib import Path


class ValidWordsStatsExporter:
    """
    Exporta `valid_words_stats` a JSON y CSV usando la misma estructura
    analítica que consume el plotter.
    """

    def __init__(self, output_dir="quarterly_valid_words"):
        self.output_dir = Path(output_dir)

    def export(self, valid_words_stats):
        """
        Genera:
        - Un JSON por quarter y speaker_group
        - Un CSV detallado por quarter y speaker_group
        - Un CSV resumen por speaker_group

        Args:
            valid_words_stats (dict): Estructura devuelta por
                process_valid_words_by_age_group(...)

        Returns:
            dict: Rutas generadas
        """
        outputs = {
            "adults": {},
            "children": {},
        }

        summary_rows = {
            "adults": [],
            "children": [],
        }

        for speaker_group in ("adults", "children"):
            group_dir = self.output_dir / speaker_group
            group_dir.mkdir(parents=True, exist_ok=True)

            for quarter, quarter_stats in sorted(valid_words_stats.items()):
                group_stats = quarter_stats[speaker_group]
                payload = self._build_payload(quarter, speaker_group, group_stats)
                json_path = group_dir / f"{quarter}.json"
                csv_path = group_dir / f"{quarter}.csv"

                self._write_json(json_path, payload)
                self._write_csv(csv_path, payload["rows"])

                outputs[speaker_group][quarter] = {
                    "json": str(json_path),
                    "csv": str(csv_path),
                }
                summary_rows[speaker_group].append(payload["summary"])

            summary_path = group_dir / "summary.csv"
            self._write_summary_csv(summary_path, summary_rows[speaker_group])
            outputs[speaker_group]["summary"] = str(summary_path)

        return outputs

    def _build_payload(self, quarter, speaker_group, group_stats):
        total_words = group_stats["total_words"]
        total_iconic = group_stats["total_iconic_occurrences"]
        total_non_iconic = group_stats["total_non_iconic_occurrences"]

        summary = {
            "quarter": quarter,
            "speaker_group": speaker_group,
            "total_words": total_words,
            "total_iconic_occurrences": total_iconic,
            "total_non_iconic_occurrences": total_non_iconic,
            "unique_iconic_words": len(group_stats["unique_iconic_words"]),
            "unique_non_iconic_words": len(group_stats["unique_non_iconic_words"]),
            "iconic_percentage": (total_iconic / total_words * 100) if total_words else 0,
            "non_iconic_percentage": (total_non_iconic / total_words * 100) if total_words else 0,
        }

        rows = []
        for word, word_data in sorted(group_stats["iconic_words"].items()):
            rows.append(
                {
                    "quarter": quarter,
                    "speaker_group": speaker_group,
                    "word": word,
                    "count": word_data["count"],
                    "is_iconic": True,
                    "rating": word_data["rating"],
                }
            )

        for word, count in sorted(group_stats["non_iconic_words"].items()):
            rows.append(
                {
                    "quarter": quarter,
                    "speaker_group": speaker_group,
                    "word": word,
                    "count": count,
                    "is_iconic": False,
                    "rating": "",
                }
            )

        rows = sorted(
            rows,
            key=lambda row: (-row["count"], row["word"]),
        )
        for index, row in enumerate(rows, start=1):
            row["id"] = index

        return {
            "quarter": quarter,
            "speaker_group": speaker_group,
            "total_rows": len(rows),
            "summary": summary,
            "rows": rows,
        }

    def _write_json(self, file_path, payload):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def _write_csv(self, file_path, rows):
        fieldnames = ["quarter", "speaker_group", "id", "word", "count", "is_iconic", "rating"]
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _write_summary_csv(self, file_path, rows):
        fieldnames = [
            "quarter",
            "speaker_group",
            "total_words",
            "total_iconic_occurrences",
            "total_non_iconic_occurrences",
            "unique_iconic_words",
            "unique_non_iconic_words",
            "iconic_percentage",
            "non_iconic_percentage",
        ]
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
