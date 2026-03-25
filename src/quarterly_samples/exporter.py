import os


class QuarterlySampleExporter:
    """
    Exporta las expresiones agrupadas por quarter a ficheros de texto
    separados para adultos y niños.
    """

    def __init__(self, output_dir="quarterly_samples"):
        self.output_dir = output_dir

    def export(self, grouped_data):
        """
        Crea una estructura:
        output_dir/
            adults/
                00Y01Q.txt
                ...
            children/
                00Y01Q.txt
                ...

        Cada fichero contiene una expresión por línea.

        Args:
            grouped_data (dict): Datos agrupados por quarter

        Returns:
            dict: Rutas de salida por grupo y quarter
        """
        adults_dir = os.path.join(self.output_dir, "adults")
        children_dir = os.path.join(self.output_dir, "children")

        os.makedirs(adults_dir, exist_ok=True)
        os.makedirs(children_dir, exist_ok=True)

        exported_files = {
            "adults": {},
            "children": {},
        }

        for age_group, data in sorted(grouped_data.items()):
            adults_path = os.path.join(adults_dir, f"{age_group}.txt")
            children_path = os.path.join(children_dir, f"{age_group}.txt")

            self._write_utterances(adults_path, data.get("adults_data", {}))
            self._write_utterances(children_path, data.get("children_data", {}))

            exported_files["adults"][age_group] = adults_path
            exported_files["children"][age_group] = children_path

        return exported_files

    def _write_utterances(self, file_path, utterances):
        with open(file_path, "w", encoding="utf-8") as file:
            for utterance in utterances.values():
                text = utterance.get("text", "").strip()
                if text:
                    file.write(f"{text}\n")
