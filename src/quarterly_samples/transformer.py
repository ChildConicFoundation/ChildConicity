import csv
import json
from pathlib import Path


class QuarterlySampleTransformer:
    """
    Lee los .txt de quarters y genera formatos derivados.
    """

    def __init__(self, base_dir="quarterly_samples"):
        self.base_dir = Path(base_dir)

    def transform(self):
        """
        Walks adult and child .txt files and generates .json and .csv files
        in the same directory.

        Returns:
            dict: Output paths by group, quarter, and format
        """
        outputs = {
            "adults": {},
            "children": {},
            "other_children": {},
        }

        for speaker_group in ("adults", "children", "other_children"):
            group_dir = self.base_dir / speaker_group
            if not group_dir.exists():
                continue

            for txt_path in sorted(group_dir.glob("*.txt")):
                quarter = txt_path.stem
                records = self._read_txt_records(txt_path, speaker_group, quarter)
                json_path = group_dir / f"{quarter}.json"
                csv_path = group_dir / f"{quarter}.csv"

                self._write_json(json_path, records)
                self._write_csv(csv_path, records)

                outputs[speaker_group][quarter] = {
                    "txt": str(txt_path),
                    "json": str(json_path),
                    "csv": str(csv_path),
                }

        return outputs

    def _read_txt_records(self, txt_path, speaker_group, quarter):
        records = []
        with open(txt_path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                text = line.rstrip("\n").strip()
                if not text:
                    continue
                records.append(
                    {
                        "quarter": quarter,
                        "speaker_group": speaker_group,
                        "line_number": line_number,
                        "text": text,
                    }
                )
        return records

    def _write_json(self, file_path, records):
        payload = {
            "quarter": file_path.stem,
            "speaker_group": file_path.parent.name,
            "total_rows": len(records),
            "rows": records,
        }
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def _write_csv(self, file_path, records):
        fieldnames = ["quarter", "speaker_group", "line_number", "text"]
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
