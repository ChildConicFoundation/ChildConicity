from src.data_io.reader import Reader

class DataFormatter:
    def __init__(self):
        self.reader = Reader()
        self.children_data = {}
        self.other_children_data = {}
        self.adults_data = {}
        self.data_dict = {}
    
    def classify_speaker(
        self,
        speaker_code,
        target_child_speakers=None,
        other_child_speakers=None,
    ):
        """
        Clasifica al hablante como niño objetivo, otro niño o adulto.
        
        Args:
            speaker_code (str): Código del hablante
            
        Returns:
            str: "target_child", "other_child" o "adult"
        """
        if target_child_speakers is None:
            target_child_speakers = {"CHI"}
        if other_child_speakers is None:
            other_child_speakers = set()

        if speaker_code in target_child_speakers:
            return "target_child"
        if speaker_code in other_child_speakers:
            return "other_child"
        return "adult"

    def is_children(self, speaker_code, child_speakers=None):
        if child_speakers is None:
            child_speakers = {"CHI"}
        return speaker_code in child_speakers
    
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
            tuple: (children_data, other_children_data, adults_data)
        """
        data = self.reader.read_cha(file_path)
        if data is not None:
            utterances = data['metadata']['utterances']
            target_child_speakers = set(
                data['metadata'].get('target_child_speakers', ['CHI'])
            )
            other_child_speakers = set(
                data['metadata'].get('other_child_speakers', [])
            )
            # Inicializar contadores independientes
            child_counter = 1
            other_child_counter = 1
            adult_counter = 1
            # Separar las expresiones por hablante
            for utterance in utterances:
                entry = {
                    'speaker': utterance['speaker'],
                    'text': utterance['text'],
                    'timestamp': utterance['timestamp']
                }
                speaker_group = self.classify_speaker(
                    utterance['speaker'],
                    target_child_speakers,
                    other_child_speakers,
                )
                if speaker_group == "target_child":
                    self.children_data[child_counter] = entry
                    child_counter += 1
                elif speaker_group == "other_child":
                    self.other_children_data[other_child_counter] = entry
                    other_child_counter += 1
                else:
                    self.adults_data[adult_counter] = entry
                    adult_counter += 1
            return self.children_data, self.other_children_data, self.adults_data
        return None, None, None
    
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

    def get_other_children_data(self):
        """
        Devuelve el diccionario con los datos de otros niños presentes.

        Returns:
            dict: Diccionario con los datos de otros niños
        """
        return self.other_children_data
    
    def get_data(self):
        """
        Devuelve el diccionario con todos los datos (para archivos CSV).
        
        Returns:
            dict: Diccionario con todos los datos
        """
        return self.data_dict 
