class IconicityModel:
    def __init__(self, data_dict):
        """
        Inicializa el modelo con los datos del CSV.
        
        Args:
            data_dict (dict): Diccionario con las entradas del CSV que contienen al menos:
                - word: palabra
                - n_ratings: número de valoraciones
                - n: número de participantes
                - prop_known: proporción de participantes que conocen la palabra
                - rating: valoración media
                - rating_sd: desviación estándar de la valoración
        """
        self.word_data = {}
        print(f"\nDepuración - Total de entradas recibidas: {len(data_dict)}")
        if len(data_dict) > 0:
            first_entry = next(iter(data_dict.values()))
            print("\nDepuración - Primera entrada recibida:")
            for key, value in first_entry.items():
                print(f"{key}: {value}")
        self._process_data(data_dict)
    
    def _process_data(self, data_dict):
        """
        Procesa los datos del diccionario y los organiza por palabra.
        
        Args:
            data_dict (dict): Diccionario con las entradas del CSV
        """
        for entry_id, entry in data_dict.items():
            if all(key in entry for key in ['word', 'n_ratings', 'n', 'prop_known', 'rating', 'rating_sd']):
                word = entry['word']
                self.word_data[word] = {
                    'n_ratings': entry['n_ratings'],
                    'n': entry['n'],
                    'prop_known': entry['prop_known'],
                    'rating': entry['rating'],
                    'rating_sd': entry['rating_sd']
                }
            else:
                print(f"\nDepuración - Entrada {entry_id} no tiene todos los campos requeridos:")
                for key, value in entry.items():
                    print(f"{key}: {value}")
        
        print(f"\nDepuración - Total de palabras procesadas: {len(self.word_data)}")
    
    def get_word_data(self, word):
        """
        Obtiene los datos de una palabra específica.
        
        Args:
            word (str): Palabra a buscar
            
        Returns:
            dict: Datos de la palabra o None si no existe
        """
        return self.word_data.get(word)
    
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
            rating = data['rating']
            if (min_rating is None or rating >= min_rating) and \
               (max_rating is None or rating <= max_rating):
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
            prop = data['prop_known']
            if (min_prop is None or prop >= min_prop) and \
               (max_prop is None or prop <= max_prop):
                filtered_words[word] = data
        return filtered_words
    
    def get_all_word_data(self):
        """
        Devuelve el diccionario completo con todos los datos de todas las palabras.
        
        Returns:
            dict: Diccionario donde las claves son las palabras y los valores son
                 diccionarios con todos sus datos (n_ratings, n, prop_known, rating, rating_sd)
        """
        return self.word_data 