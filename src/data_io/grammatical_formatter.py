from src.data_io.reader import Reader


class GrammaticalDataFormatter:
    def __init__(self):
        self.reader = Reader()

    def is_children(self, speaker_code):
        return speaker_code == "CHI"

    def format_cha_data_from(self, file_path):
        """
        Formatea los datos morfológicos de un archivo .cha separándolos
        en niños y adultos.
        """
        data = self.reader.read_cha(file_path)
        if data is None:
            return None, None

        children_data = {}
        adults_data = {}
        morphological_utterances = data["metadata"]["morphological_utterances"]
        child_counter = 1
        adult_counter = 1

        for utterance in morphological_utterances:
            for token in utterance["tokens"]:
                entry = {
                    "speaker": utterance["speaker"],
                    "category": token["category"],
                    "lemma": token["lemma"],
                    "attributes": token["attributes"],
                    "raw_token": token["raw_token"],
                    "timestamp": utterance["timestamp"],
                }

                if self.is_children(utterance["speaker"]):
                    children_data[child_counter] = entry
                    child_counter += 1
                else:
                    adults_data[adult_counter] = entry
                    adult_counter += 1

        return children_data, adults_data
