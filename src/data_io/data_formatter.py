from src.data_io.reader import Reader

class DataFormatter:
    def __init__(self):
        self.reader = Reader()
        self.children_data = {}
        self.adults_data = {}
        self.data_dict = {}
    
    def is_children(self, speaker_code):
        """
        Determina si el hablante es un niño basándose en su código.
        
        Args:
            speaker_code (str): Código del hablante
            
        Returns:
            bool: True si es un niño, False en caso contrario
        """
        return speaker_code == 'CHI'
    
    def format_csv_data_from(self, file_path):
        """
        Formatea los datos de un archivo CSV.
        
        Args:
            file_path (str): Ruta del archivo CSV a leer
            
        Returns:
            dict: Diccionario con los datos formateados
        """
        data = self.reader.read_csv(file_path)
        if data is not None:
            self.data_dict = {i+1: entry for i, entry in enumerate(data.to_dict('records'))}
            return self.data_dict
        return None
    
    def format_cha_data_from(self, file_path):
        """
        Formatea los datos de un archivo .cha.
        
        Args:
            file_path (str): Ruta del archivo .cha a leer
            
        Returns:
            tuple: (children_data, adults_data) - Diccionarios con los datos separados por niños y adultos
        """
        data = self.reader.read_cha(file_path)
        if data is not None:
            utterances = data['metadata']['utterances']
            # Inicializar contadores independientes
            child_counter = 1
            adult_counter = 1
            # Separar las expresiones por hablante
            for utterance in utterances:
                entry = {
                    'speaker': utterance['speaker'],
                    'text': utterance['text'],
                    'timestamp': utterance['timestamp']
                }
                if self.is_children(utterance['speaker']):
                    self.children_data[child_counter] = entry
                    child_counter += 1
                else:
                    self.adults_data[adult_counter] = entry
                    adult_counter += 1
            return self.children_data, self.adults_data
        return None, None
    
    def get_children_data(self):
        """
        Devuelve el diccionario con los datos de los niños.
        
        Returns:
            dict: Diccionario con los datos de los niños
        """
        return self.children_data
    
    def get_adults_data(self):
        """
        Devuelve el diccionario con los datos de los adultos.
        
        Returns:
            dict: Diccionario con los datos de los adultos
        """
        return self.adults_data
    
    def get_data(self):
        """
        Devuelve el diccionario con todos los datos (para archivos CSV).
        
        Returns:
            dict: Diccionario con todos los datos
        """
        return self.data_dict 