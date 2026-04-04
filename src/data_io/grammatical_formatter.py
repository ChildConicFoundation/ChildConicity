from src.data_io.reader import Reader


class GrammaticalDataFormatter:
    def __init__(self, grammatical_categories=None):
        self.reader = Reader()
        self.grammatical_categories = self._normalize_categories(
            grammatical_categories
        )

    def _normalize_categories(self, grammatical_categories):
        if grammatical_categories is None:
            return None

        if isinstance(grammatical_categories, str):
            grammatical_categories = [grammatical_categories]

        normalized_categories = {
            category.strip().casefold()
            for category in grammatical_categories
            if category and category.strip()
        }

        if not normalized_categories or "all" in normalized_categories:
            return None

        return normalized_categories

    def _should_include_category(self, category):
        if self.grammatical_categories is None:
            return True

        return category.casefold() in self.grammatical_categories

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

        return self.format_morphological_utterances(
            data["metadata"]["morphological_utterances"]
        )

    def format_morphological_utterances(self, morphological_utterances):
        children_data = {}
        adults_data = {}
        child_counter = 1
        adult_counter = 1

        for utterance in morphological_utterances:
            for token in utterance["tokens"]:
                if not self._should_include_category(token["category"]):
                    continue

                entry = self._build_entry(utterance, token)

                if self.is_children(utterance["speaker"]):
                    children_data[child_counter] = entry
                    child_counter += 1
                else:
                    adults_data[adult_counter] = entry
                    adult_counter += 1

        return children_data, adults_data

    def _build_entry(self, utterance, token):
        return {
            "speaker": utterance["speaker"],
            "category": token["category"],
            "lemma": token["lemma"],
            "attributes": token["attributes"],
            "raw_token": token["raw_token"],
            "timestamp": utterance["timestamp"],
        }
