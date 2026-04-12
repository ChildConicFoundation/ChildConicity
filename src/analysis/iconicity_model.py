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
        Inicializa el modelo con los datos del CSV.

        Las palabras se normalizan a minúsculas para que casen con el
        tokenizado del pipeline.
        """
        self.word_data = {}
        self._process_data(data_dict or {})

    def _process_data(self, data_dict):
        """
        Procesa los datos del diccionario y los organiza por palabra.
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
        Obtiene los datos de una palabra específica.

        Args:
            word (str): Palabra a buscar

        Returns:
            dict: Datos de la palabra o None si no existe
        """
        return self.word_data.get(self._normalize_word(word))

    def get_all_words(self):
        """
        Obtiene todas las palabras en el modelo.

        Returns:
            list: Lista de todas las palabras
        """
        return list(self.word_data.keys())

    def get_words_by_rating(self, min_rating=None, max_rating=None):
        """
        Obtiene las palabras filtradas por rango de valoración.

        Args:
            min_rating (float): Valoración mínima (opcional)
            max_rating (float): Valoración máxima (opcional)

        Returns:
            dict: Diccionario con las palabras y sus datos que cumplen el criterio
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
        Obtiene las palabras filtradas por rango de proporción de conocimiento.

        Args:
            min_prop (float): Proporción mínima (opcional)
            max_prop (float): Proporción máxima (opcional)

        Returns:
            dict: Diccionario con las palabras y sus datos que cumplen el criterio
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
        Devuelve el diccionario completo con todos los datos de todas las palabras.

        Returns:
            dict: Diccionario donde las claves son las palabras y los valores son
                 diccionarios con todos sus datos.
        """
        return self.word_data
