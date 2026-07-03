class IconicityModel:
    REQUIRED_FIELDS = {
        "word",
        "n_ratings",
        "n",
        "prop_known",
        "rating",
        "rating_sd",
    }

    def __init__(self, data_dict):
        """
        Initializes the model with CSV data.

        Words are normalized to lowercase so they match the
        pipeline tokenization.
        """
        self.word_data = {}
        self._process_data(data_dict or {})

    def _process_data(self, data_dict):
        """
        Processes dictionary data and organizes it by word.
        """
        for entry in data_dict.values():
            if not self.REQUIRED_FIELDS.issubset(entry):
                continue

            normalized_word = self._normalize_word(entry["word"])
            if not normalized_word:
                continue

            normalized_entry = {
                "n_ratings": entry["n_ratings"],
                "n": entry["n"],
                "prop_known": entry["prop_known"],
                "rating": entry["rating"],
                "rating_sd": entry["rating_sd"],
            }

            existing_entry = self.word_data.get(normalized_word)
            if (
                existing_entry is None
                or self._entry_priority(normalized_entry)
                > self._entry_priority(existing_entry)
            ):
                self.word_data[normalized_word] = normalized_entry

    def _normalize_word(self, word):
        if not isinstance(word, str):
            return ""

        return word.strip().lower()

    def _entry_priority(self, entry):
        return (
            self._safe_float(entry.get("n_ratings")),
            self._safe_float(entry.get("prop_known")),
            self._safe_float(entry.get("rating")),
        )

    def _safe_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return float("-inf")

    def get_word_data(self, word):
        """
        Gets data for a specific word.

        Args:
            word (str): Word to search for

        Returns:
            dict: Word data or None if it does not exist
        """
        return self.word_data.get(self._normalize_word(word))

    def get_all_words(self):
        """
        Gets all words in the model.

        Returns:
            list: List of all words
        """
        return list(self.word_data.keys())

    def get_words_by_rating(self, min_rating=None, max_rating=None):
        """
        Gets words filtered by rating range.

        Args:
            min_rating (float): Minimum rating (optional)
            max_rating (float): Maximum rating (optional)

        Returns:
            dict: Dictionary with words and data matching the criterion
        """
        filtered_words = {}
        for word, data in self.word_data.items():
            rating = data["rating"]
            if (min_rating is None or rating >= min_rating) and (
                max_rating is None or rating <= max_rating
            ):
                filtered_words[word] = data
        return filtered_words

    def get_words_by_known_proportion(self, min_prop=None, max_prop=None):
        """
        Gets words filtered by knowledge proportion range.

        Args:
            min_prop (float): Minimum proportion (optional)
            max_prop (float): Maximum proportion (optional)

        Returns:
            dict: Dictionary with words and data matching the criterion
        """
        filtered_words = {}
        for word, data in self.word_data.items():
            prop = data["prop_known"]
            if (min_prop is None or prop >= min_prop) and (
                max_prop is None or prop <= max_prop
            ):
                filtered_words[word] = data
        return filtered_words

    def get_all_word_data(self):
        """
        Returns the full dictionary with all data for all words.

        Returns:
            dict: Dictionary where keys are words and values are
                 dictionaries with all their data.
        """
        return self.word_data
