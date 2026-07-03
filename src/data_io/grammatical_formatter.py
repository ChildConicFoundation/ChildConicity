from src.data_io.reader import Reader


class GrammaticalDataFormatter:
    def __init__(self, grammatical_categories=None):
        self.reader = Reader()
        self.grammatical_categories = self._normalize_categories(
            grammatical_categories
        )
        self.last_mlu_stats = self._empty_mlu_stats()

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

    def classify_speaker(
        self,
        speaker_code,
        target_child_speakers=None,
        other_child_speakers=None,
    ):
        if target_child_speakers is None:
            target_child_speakers = {"CHI"}
        if other_child_speakers is None:
            other_child_speakers = set()

        if speaker_code in target_child_speakers:
            return "target_child"
        if speaker_code in other_child_speakers:
            return "other_child"
        return "adult"

    def format_cha_data_from(self, file_path):
        """
        Formats morphological data from a .cha file, separating it
        into child and adult data.
        """
        data = self.reader.read_cha(file_path)
        if data is None:
            return None, None, None

        morphological_utterances = data["metadata"]["morphological_utterances"]
        target_child_speakers = set(
            data["metadata"].get("target_child_speakers", ["CHI"])
        )
        other_child_speakers = set(data["metadata"].get("other_child_speakers", []))

        return self.format_morphological_utterances(
            morphological_utterances,
            target_child_speakers,
            other_child_speakers,
        )

    def format_morphological_utterances(
        self,
        morphological_utterances,
        target_child_speakers=None,
        other_child_speakers=None,
    ):
        children_data = {}
        other_children_data = {}
        adults_data = {}
        child_counter = 1
        other_child_counter = 1
        adult_counter = 1

        self.last_mlu_stats = self._calculate_mlu_stats(
            morphological_utterances,
            target_child_speakers,
            other_child_speakers,
        )

        for utterance_index, utterance in enumerate(morphological_utterances, start=1):
            for token in utterance["tokens"]:
                if not self._should_include_category(token["category"]):
                    continue

                entry = self._build_entry(utterance, token, utterance_index)

                speaker_group = self.classify_speaker(
                    utterance["speaker"],
                    target_child_speakers,
                    other_child_speakers,
                )
                if speaker_group == "target_child":
                    children_data[child_counter] = entry
                    child_counter += 1
                elif speaker_group == "other_child":
                    other_children_data[other_child_counter] = entry
                    other_child_counter += 1
                else:
                    adults_data[adult_counter] = entry
                    adult_counter += 1

        return children_data, other_children_data, adults_data

    def _build_entry(self, utterance, token, utterance_index):
        return {
            "speaker": utterance["speaker"],
            "utterance_id": utterance_index,
            "utterance_morpheme_count": self._count_utterance_morphemes(utterance),
            "category": token["category"],
            "lemma": token["lemma"],
            "attributes": token["attributes"],
            "raw_token": token["raw_token"],
            "timestamp": utterance["timestamp"],
        }

    def _calculate_mlu_stats(
        self,
        morphological_utterances,
        target_child_speakers=None,
        other_child_speakers=None,
    ):
        stats = self._empty_mlu_stats()

        for utterance in morphological_utterances:
            morpheme_count = self._count_utterance_morphemes(utterance)
            if morpheme_count == 0:
                continue

            speaker_group = self.classify_speaker(
                utterance["speaker"],
                target_child_speakers,
                other_child_speakers,
            )
            output_group = self._speaker_group_to_output_group(speaker_group)
            stats[output_group]["morpheme_count"] += morpheme_count
            stats[output_group]["utterance_count"] += 1

        return stats

    def _count_utterance_morphemes(self, utterance):
        return len(utterance.get("tokens", []))

    def _speaker_group_to_output_group(self, speaker_group):
        if speaker_group == "target_child":
            return "children"
        if speaker_group == "other_child":
            return "other_children"
        return "adults"

    def _empty_mlu_stats(self):
        return {
            "children": {"morpheme_count": 0, "utterance_count": 0},
            "other_children": {"morpheme_count": 0, "utterance_count": 0},
            "adults": {"morpheme_count": 0, "utterance_count": 0},
        }
