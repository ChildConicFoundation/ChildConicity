import os


class QuarterlySampleExporter:
    """
    Exports utterances grouped by quarter to text files
    separated for adults and children.
    """

    def __init__(self, output_dir="quarterly_samples"):
        self.output_dir = output_dir

    def export(self, grouped_data):
        """
        Creates a structure:
        output_dir/
            adults/
                00Y01Q.txt
                ...
            children/
            other_children/
                00Y01Q.txt
                ...

        Each file contains one utterance per line.

        Args:
            grouped_data (dict): Data grouped by quarter

        Returns:
            dict: Output paths by group and quarter
        """
        adults_dir = os.path.join(self.output_dir, "adults")
        children_dir = os.path.join(self.output_dir, "children")
        other_children_dir = os.path.join(self.output_dir, "other_children")

        os.makedirs(adults_dir, exist_ok=True)
        os.makedirs(children_dir, exist_ok=True)
        os.makedirs(other_children_dir, exist_ok=True)

        exported_files = {
            "adults": {},
            "children": {},
            "other_children": {},
        }

        for age_group, data in sorted(grouped_data.items()):
            adults_path = os.path.join(adults_dir, f"{age_group}.txt")
            children_path = os.path.join(children_dir, f"{age_group}.txt")
            other_children_path = os.path.join(
                other_children_dir, f"{age_group}.txt"
            )

            self._write_utterances(adults_path, data.get("adults_data", {}))
            self._write_utterances(children_path, data.get("children_data", {}))
            self._write_utterances(
                other_children_path,
                data.get("other_children_data", {}),
            )

            exported_files["adults"][age_group] = adults_path
            exported_files["children"][age_group] = children_path
            exported_files["other_children"][age_group] = other_children_path

        return exported_files

    def _write_utterances(self, file_path, utterances):
        with open(file_path, "w", encoding="utf-8") as file:
            for utterance in utterances.values():
                text = utterance.get("text", "").strip()
                if text:
                    file.write(f"{text}\n")
