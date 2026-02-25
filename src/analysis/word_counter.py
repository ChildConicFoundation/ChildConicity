import re
from collections import defaultdict

class WordCounter:
    """
    Clase para contar palabras en un texto.
    """
    
    def __init__(self):
        """
        Inicializa el contador de palabras.
        """
        self.word_counts = defaultdict(int)
    
    def count_words(self, data):
        """
        Cuenta las palabras en el texto proporcionado.
        
        Args:
            data (str or dict): String con texto o diccionario con campos 'text' para procesar.
        """
        # Si data es un string, procesarlo directamente
        if isinstance(data, str):
            words = re.findall(r'\b\w+\b', data.lower())
            for word in words:
                self.word_counts[word] += 1
        # Si data es un diccionario, procesar cada entrada
        elif isinstance(data, dict):
            if 'text' in data:
                words = re.findall(r'\b\w+\b', data['text'].lower())
                for word in words:
                    self.word_counts[word] += 1
            else:
                for entry in data.values():
                    if isinstance(entry, dict) and 'text' in entry:
                        words = re.findall(r'\b\w+\b', entry['text'].lower())
                        for word in words:
                            self.word_counts[word] += 1
    
    def get_word_counts(self):
        """
        Obtiene el diccionario de conteo de palabras.
        
        Returns:
            dict: Diccionario con palabras como claves y diccionarios con conteos como valores.
        """
        result = {}
        for word, count in self.word_counts.items():
            result[word] = {'count': count}
        return result
    
    def get_most_common(self, n=10):
        """
        Obtiene las n palabras más comunes.
        
        Args:
            n (int): Número de palabras a retornar.
            
        Returns:
            list: Lista de tuplas (palabra, conteo) ordenadas por frecuencia.
        """
        # Ordenar por conteo y luego alfabéticamente para desempates
        return sorted(self.word_counts.items(), 
                     key=lambda x: (-x[1], x[0]))[:n]
    
    def clear(self):
        """
        Limpia el contador de palabras.
        """
        self.word_counts.clear() 