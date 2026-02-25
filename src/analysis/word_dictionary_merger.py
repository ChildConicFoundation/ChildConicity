class WordDictionaryMerger:
    def __init__(self):
        """
        Inicializa el merger con un array vacío de diccionarios.
        """
        self.dictionaries = []
    
    def add_dictionary(self, dictionary):
        """
        Añade un nuevo diccionario al array.
        
        Args:
            dictionary (dict): Diccionario que tiene strings como claves principales
        """
        if not isinstance(dictionary, dict):
            raise ValueError("El parámetro debe ser un diccionario")
        self.dictionaries.append(dictionary)
    
    def sort_by_parameter(self, parameter, comparison_op, threshold=None):
        """
        Ordena las palabras basándose en un parámetro y una operación de comparación.
        
        Args:
            parameter (str): Nombre del parámetro por el que se quiere ordenar
            comparison_op (str): Operación de comparación ('gt' para mayor que, 'lt' para menor que)
            threshold (float, optional): Valor umbral para la comparación
            
        Returns:
            dict: Diccionario con las palabras que cumplen la condición, ordenadas por el parámetro
        """
        if not self.dictionaries:
            return {}
            
        # Obtener todas las palabras y sus datos
        all_words_data = {}
        for dictionary in self.dictionaries:
            for word, data in dictionary.items():
                if word not in all_words_data:
                    all_words_data[word] = data
                else:
                    all_words_data[word].update(data)
        
        # Filtrar y ordenar según la condición
        filtered_words = {}
        for word, data in all_words_data.items():
            if parameter in data:
                value = data[parameter]
                if isinstance(value, (int, float)):
                    if comparison_op == 'gt' and (threshold is None or value > threshold):
                        filtered_words[word] = data
                    elif comparison_op == 'lt' and (threshold is None or value < threshold):
                        filtered_words[word] = data
        
        # Ordenar el diccionario por el parámetro
        sorted_words = dict(sorted(
            filtered_words.items(),
            key=lambda x: x[1][parameter],
            reverse=(comparison_op == 'gt')
        ))
        
        return sorted_words
    
    def obtain_merge(self):
        """
        Obtiene dos resultados:
        1. Un diccionario con las palabras que aparecen en todos los diccionarios, mergeando sus datos
        2. Un array con los diccionarios de palabras que no se pudieron mergear
        
        Returns:
            tuple: (merged_dict, unmerged_dictionaries)
        """
        if not self.dictionaries:
            return {}, []
        
        # Obtener todas las palabras únicas
        all_words = set()
        for dictionary in self.dictionaries:
            all_words.update(dictionary.keys())
        
        # Encontrar palabras comunes a todos los diccionarios
        common_words = set(all_words)
        for dictionary in self.dictionaries:
            common_words.intersection_update(dictionary.keys())
        
        # Crear el diccionario mergeado
        merged_dict = {}
        for word in common_words:
            merged_data = {}
            for dictionary in self.dictionaries:
                merged_data.update(dictionary[word])
            merged_dict[word] = merged_data
        
        # Crear los diccionarios no mergeados
        unmerged_dictionaries = []
        for dictionary in self.dictionaries:
            unmerged_dict = {}
            for word, data in dictionary.items():
                if word not in common_words:
                    unmerged_dict[word] = data
            if unmerged_dict:  # Solo añadir si hay palabras no mergeadas
                unmerged_dictionaries.append(unmerged_dict)
        
        return merged_dict, unmerged_dictionaries 