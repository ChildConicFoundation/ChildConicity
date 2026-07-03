from src.data_io.reader import Reader

class DataFormatter:
    def __init__(self):
        self.reader = Reader()
        self.children_data = {}
        self.other_children_data = {}
        self.adults_data = {}
        self.data_dict = {}

    def _reset_cha_state(self):
        self.children_data = {}
        self.other_children_data = {}
        self.adults_data = {}
    
    def classify_speaker(
        self,
        speaker_code,
        target_child_speakers=None,
        other_child_speakers=None,
    ):
        """
        Classifies the speaker as target child, other child, or adult.
        
        Args:
            speaker_code (str): Speaker code
            
        Returns:
            str: "target_child", "other_child", or "adult"
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
        Formats data from a CSV file.
        
        Args:
            file_path (str): Path to the CSV file to read
            
        Returns:
            dict: Dictionary with formatted data
        """
        data = self.reader.read_csv(file_path)
        if data is not None:
            self.data_dict = {i+1: entry for i, entry in enumerate(data.to_dict('records'))}
            return self.data_dict
        return None
    
    def format_cha_data_from(self, file_path):
        """
        Formats data from a .cha file.
        
        Args:
            file_path (str): Path to the .cha file to read
            
        Returns:
            tuple: (children_data, other_children_data, adults_data)
        """
        self._reset_cha_state()
        data = self.reader.read_cha(file_path)
        if data is not None:
            utterances = data['metadata']['utterances']
            target_child_speakers = set(
                data['metadata'].get('target_child_speakers', ['CHI'])
            )
            other_child_speakers = set(
                data['metadata'].get('other_child_speakers', [])
            )
            # Initialize independent counters
            child_counter = 1
            other_child_counter = 1
            adult_counter = 1
            # Separate utterances by speaker
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
        Returns the dictionary with child data.
        
        Returns:
            dict: Dictionary with child data
        """
        return self.children_data
    
    def get_adults_data(self):
        """
        Returns the dictionary with adult data.
        
        Returns:
            dict: Dictionary with adult data
        """
        return self.adults_data

    def get_other_children_data(self):
        """
        Returns the dictionary with data for other children present.

        Returns:
            dict: Dictionary with data for other children
        """
        return self.other_children_data
    
    def get_data(self):
        """
        Returns the dictionary with all data for CSV files.
        
        Returns:
            dict: Dictionary with all data
        """
        return self.data_dict 
