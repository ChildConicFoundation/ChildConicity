import re
import os

TARGET_CHILD_PARTICIPANT_ROLES = {
    "target_child",
}

OTHER_CHILD_PARTICIPANT_ROLES = {
    "child",
    "sibling",
    "sister",
    "brother",
    "playmate",
}


class Reader:
    def __init__(self):
        self.data = None
    
    def read_csv(self, file_path):
        """
        Reads a CSV file and stores it in the data attribute.
        
        Args:
            file_path (str): Path to the CSV file to read
            
        Returns:
            pandas.DataFrame: The data read from the CSV file
        """
        try:
            import pandas as pd

            self.data = pd.read_csv(file_path)
            return self.data
        except ModuleNotFoundError:
            print(
                "Error: pandas no está instalado y es necesario para leer archivos CSV."
            )
            return None
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {file_path}")
            return None
        except Exception as e:
            print(f"Error al leer el archivo CSV: {str(e)}")
            return None

    def read_cha(self, file_path):
        """
        Reads a .cha file and converts it to a structured format.
        
        Args:
            file_path (str): Path to the .cha file to read
            
        Returns:
            dict: Dictionary with structured data from the .cha file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Extract file metadata
            metadata = {
                'file_path': file_path,
                'file_type': 'cha',
                'encoding': self._extract_encoding(content),
                'pid': self._extract_pid(content),
                'languages': self._extract_languages(content),
                'participants': self._extract_participants(content),
                'options': self._extract_options(content),
                'media': self._extract_media(content),
                'date': self._extract_date(content),
                'child_age': self._extract_child_age(content),
                'child_name': self._extract_child_name(content),
                'participant_roles': self._extract_participant_roles(content),
                'target_child_speakers': self._extract_target_child_speakers(content),
                'other_child_speakers': self._extract_other_child_speakers(content),
                'child_speakers': self._extract_child_speakers(content),
                'types': self._extract_types(content),
                'utterances': self._extract_utterances(content),
                'morphological_utterances': self._extract_morphological_utterances(content),
            }
            
            self.data = {
                'content': content,
                'metadata': metadata
            }
            return self.data
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {file_path}")
            return None
        except Exception as e:
            print(f"Error al leer el archivo .cha: {str(e)}")
            return None

    def _extract_encoding(self, content):
        """Extracts the file encoding."""
        match = re.search(r'@UTF8', content)
        return 'UTF8' if match else None

    def _extract_pid(self, content):
        """Extracts the file PID."""
        match = re.search(r'@PID:\s*(.*)', content)
        return match.group(1).strip() if match else None

    def _extract_languages(self, content):
        """Extracts the file languages."""
        match = re.search(r'@Languages:\s*(.*)', content)
        return match.group(1).strip().split(',') if match else []

    def _extract_participants(self, content):
        """Extracts the file participants."""
        match = re.search(r'@Participants:\s*(.*)', content)
        if match:
            participants = {}
            for part in match.group(1).strip().split(','):
                code, name = part.strip().split(' ', 1)
                participants[code] = name
            return participants
        return {}

    def _extract_options(self, content):
        """Extracts the file options."""
        match = re.search(r'@Options:\s*(.*)', content)
        return match.group(1).strip().split(',') if match else []

    def _extract_media(self, content):
        """Extracts the file media information."""
        match = re.search(r'@Media:\s*(.*)', content)
        if match:
            media_info = match.group(1).strip().split(',')
            return {
                'id': media_info[0].strip(),
                'type': media_info[1].strip() if len(media_info) > 1 else None
            }
        return None

    def _extract_date(self, content):
        """Extracts the file date."""
        match = re.search(r'@Date:\s*(.*)', content)
        return match.group(1).strip() if match else None

    def _extract_child_age(self, content):
        """Extracts the child age from the file."""
        match = re.search(r'@ChildAge:\s*(.*)', content)
        return match.group(1).strip() if match else None

    def _extract_child_name(self, content):
        """Extracts the child name from the file."""
        # First search in @ChildName
        match = re.search(r'@ChildName:\s*(.*)', content)
        if match:
            return match.group(1).strip()
        
        # If it is not found, search participants
        participants = self._extract_participants(content)
        for code, name in participants.items():
            if 'CHI' in code:
                return name.split()[0]  # Take only the first name
        return None

    def _extract_participant_roles(self, content):
        """Extracts each participant semantic roles from @ID."""
        participant_roles = {}

        for line in content.split('\n'):
            if not line.startswith('@ID:'):
                continue

            fields = [field.strip() for field in line.split(':', 1)[1].split('|')]
            if len(fields) < 8:
                continue

            speaker_code = fields[2]
            participant_role = fields[7]
            if speaker_code:
                participant_roles[speaker_code] = participant_role

        return participant_roles

    def _extract_target_child_speakers(self, content):
        """Gets the speaker codes for the target child."""
        target_child_speakers = {"CHI"}

        for speaker_code, participant_role in self._extract_participant_roles(
            content
        ).items():
            if participant_role.casefold() in TARGET_CHILD_PARTICIPANT_ROLES:
                target_child_speakers.add(speaker_code)

        return sorted(target_child_speakers)

    def _extract_other_child_speakers(self, content):
        """Gets speaker codes for non-target child speakers."""
        other_child_speakers = set()

        for speaker_code, participant_role in self._extract_participant_roles(
            content
        ).items():
            if participant_role.casefold() in OTHER_CHILD_PARTICIPANT_ROLES:
                other_child_speakers.add(speaker_code)

        other_child_speakers.discard("CHI")
        return sorted(other_child_speakers)

    def _extract_child_speakers(self, content):
        """Gets all child speaker codes."""
        child_speakers = set(self._extract_target_child_speakers(content))
        child_speakers.update(self._extract_other_child_speakers(content))
        return sorted(child_speakers)

    def _extract_types(self, content):
        """Extracts the file types."""
        match = re.search(r'@Types:\s*(.*)', content)
        return match.group(1).strip().split(',') if match else []

    def _extract_utterances(self, content):
        """
        Extracts utterances from the file.
        Limpia las notaciones especiales como:
        - [= babble], (.), etc.
        - &=babble, &=laugh, etc.
        - Notaciones de vocalizaciones y sonidos
        """
        utterances = []
        for line in content.split('\n'):
            if line.startswith('*'):
                speaker, text = line.split(':', 1)
                speaker = speaker[1:].strip()  # Remove the asterisk
                
                # Extract the timestamp
                timestamp = self._extract_timestamp(text)
                
                # Clean the text:
                # 1. Remove timestamps
                clean_text = re.sub(r'\d+_\d+', '', text)
                
                # 2. Remove bracketed notations [= xxx]
                clean_text = re.sub(r'\[=.*?\]', '', clean_text)
                
                # 3. Remove parenthesized notations (xxx)
                clean_text = re.sub(r'\(.*?\)', '', clean_text)
                
                # 4. Remove notations that start with &= (vocalizations, sounds, etc.)
                clean_text = re.sub(r'&=\w+', '', clean_text)
                
                # 5. Remove punctuation notations (., ?, !)
                clean_text = re.sub(r'[.?!]', '', clean_text)
                
                # 6. Remove common vocalization notations
                vocalizations = [
                    r'&[a-z]+',  # Notations that start with & (&=xxx)
                    r'[<>]',     # Intonation notations
                    r'[()]',     # Standalone parentheses
                    r'[\[\]]',   # Standalone brackets
                    r'[{}]',     # Braces
                    r'[+-]',     # + and - signs
                    r'[0-9]',    # Numbers
                    r'[#@]',     # Special characters
                ]
                for pattern in vocalizations:
                    clean_text = re.sub(pattern, '', clean_text)
                
                # 7. Remove repeated spaces and leading/trailing spaces
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                # Only add the utterance if text remains after cleaning
                if clean_text:
                    utterances.append({
                        'speaker': speaker,
                        'text': clean_text,
                        'timestamp': timestamp
                    })
        return utterances

    def _extract_morphological_utterances(self, content):
        """
        Extracts morphological utterances from the file and links them
        to the speaker from the immediately preceding * line.
        """
        morphological_utterances = []
        current_speaker = None
        current_timestamp = None

        for line in content.split('\n'):
            if line.startswith('*'):
                speaker, text = line.split(':', 1)
                current_speaker = speaker[1:].strip()
                current_timestamp = self._extract_timestamp(text)
            elif line.startswith('%mor:') and current_speaker:
                mor_text = line.split(':', 1)[1].strip()
                tokens = self._parse_morphological_tokens(mor_text)
                if tokens:
                    morphological_utterances.append({
                        'speaker': current_speaker,
                        'timestamp': current_timestamp,
                        'tokens': tokens
                    })

        return morphological_utterances

    def _parse_morphological_tokens(self, mor_text):
        """
        Parses a %mor: line into structured tokens with:
        - category
        - lemma
        - attributes
        """
        tokens = []

        # Split by spaces and then by ~ to divide contractions/clitics.
        for raw_chunk in mor_text.split():
            for raw_token in raw_chunk.split('~'):
                parsed = self._parse_morphological_token(raw_token.strip())
                if parsed is not None:
                    tokens.append(parsed)

        return tokens

    def _parse_morphological_token(self, raw_token):
        if not raw_token or '|' not in raw_token:
            return None

        category, remainder = raw_token.split('|', 1)
        category = category.strip()
        remainder = remainder.strip()

        if not category or not remainder:
            return None

        # Ignore punctuation remnants or other tokens without a lemma.
        if remainder in {'.', ',', '!', '?'}:
            return None

        if '-' in remainder:
            lemma, attribute_text = remainder.split('-', 1)
            attributes = [part for part in attribute_text.split('-') if part]
        else:
            lemma = remainder
            attributes = []

        lemma = lemma.strip()
        if not lemma or lemma in {'.', ',', '!', '?'}:
            return None

        return {
            'category': category,
            'lemma': lemma,
            'attributes': attributes,
            'raw_token': raw_token,
        }

    def _extract_timestamp(self, text):
        """Extracts the timestamp from an utterance."""
        match = re.search(r'(\d+)_(\d+)', text)
        if match:
            return {
                'start': int(match.group(1)),
                'end': int(match.group(2))
            }
        return None

    def read_directory(self, directory_path):
        """
        Recursively reads all .cha files in a directory and its subdirectories.
        Creates a nested dictionary that reflects the directory structure.


        Args:
            directory_path (str): Path to the directory to read
            
        Returns:
            dict: Nested dictionary with the directory and file structure
        """
        # Get the base directory name
        base_dir = os.path.basename(directory_path)
        
        # Create the dictionary for this directory
        result = {base_dir: {}}
        
        # Walk the directory
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            
            if os.path.isdir(item_path):
                # If it is a directory, read it recursively
                subdir_content = self.read_directory(item_path)
                # Add the subdirectory contents to the current dictionary
                result[base_dir][item] = subdir_content[item]
            elif item.endswith('.cha'):
                # If it is a .cha file, read it using read_cha
                cha_content = self.read_cha(item_path)
                if cha_content:
                    # If the 'files' key does not exist, create it
                    if 'files' not in result[base_dir]:
                        result[base_dir]['files'] = []
                    result[base_dir]['files'].append(cha_content)
        
        return result 
