import os
import re
from src.data_io.data_formatter import DataFormatter

class BrendManipulator:
    """Specific manipulator for the Brend corpus"""
    
    def __init__(self):
        self.base_dir = None
        self.output_dir = None
        self.formatter = DataFormatter()
    
    def process_directory(self):
        """Processes the Brend corpus directory"""
        if not self.base_dir:
            raise ValueError("base_dir is not configured")
            
        # Process all .cha files in the directory
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith('.cha'):
                    file_path = os.path.join(root, file)
                    # Create the directory structure in output_dir
                    if self.output_dir:
                        rel_path = os.path.relpath(root, self.base_dir)
                        output_root = os.path.join(self.output_dir, rel_path)
                        os.makedirs(output_root, exist_ok=True)
                        output_path = os.path.join(output_root, file)
                    else:
                        output_path = file_path
                    
                    # Process the file
                    self.process_file(file_path, output_path)
    
    def process_file(self, input_path, output_path):
        """Processes an individual .cha file from the Brend corpus"""
        try:
            # Read the file content
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the child age and name
            age = self.extract_age(content, input_path)
            child_name = self.extract_child_name(content, input_path)
            
            # Modify the file with the extracted age and name
            modified_content = self.add_metadata_to_content(content, age, child_name)
            
            # Save the modified file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
                
            print(f"File modified successfully: {output_path}")
        except Exception as e:
            print(f"Error processing file {input_path}: {str(e)}")
    
    def extract_age(self, content, file_path=None):
        """Extracts the age from the file content and formats it as 'X years YY months ZZ days'"""
        try:
            years = 0
            months = 0
            days = 0
            
            # If the content is a file path, read the file
            if os.path.isfile(content):
                with open(content, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Special case for Brent: extract the age from the file name
            if file_path and 'Brent' in file_path:
                # The file name has the format YYMMDD.cha or m1-[r|f]DDmmmYY.cha
                file_name = os.path.basename(file_path)
                if file_name.endswith('.cha'):
                    file_name = file_name[:-4]  # Remove the .cha extension
                    
                    # Special case for m1 files
                    if file_name.startswith('m1-'):
                        # Format: m1-[r|f]DDmmmYY
                        # Ejemplo: m1-r27jul00
                        match = re.match(r'm1-[rf](\d{2})([a-z]{3})(\d{2})', file_name)
                        if match:
                            day = int(match.group(1))
                            month_str = match.group(2).lower()
                            year = int(match.group(3))
                            
                            # Convert the text month to a number
                            month_map = {
                                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                                'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                                'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                            }
                            month = month_map.get(month_str, 0)
                            
                            # Adjust the year (00 -> 2000)
                            year = 2000 + year if year < 100 else year
                            
                            return f"0 years {month:02d} months {day:02d} days"
                    
                    # Normal case: YYMMDD.cha
                    elif len(file_name) >= 6:  # Make sure it has at least 6 digits
                        years = int(file_name[0:2])
                        months = int(file_name[2:4])
                        days = int(file_name[4:6])
                        return f"{years} years {months:02d} months {days:02d} days"
            
            # For other cases, search the content
            # Search for the age in the PID
            pid_pattern = r'@PID:.*?\|(\d+);(\d+)\|'
            match = re.search(pid_pattern, content)
            if match:
                years = int(match.group(1))
                months = int(match.group(2))
                return f"{years} years {months:02d} months {days:02d} days"
            
            # Search for the age in the @ID format: eng|VanKleeck|CHI|3;09.|male|TD||Target_Child|||
            id_pattern = r'@ID:.*?CHI\|(\d+);(\d+)\.'
            match = re.search(id_pattern, content)
            if match:
                years = int(match.group(1))
                months = int(match.group(2))
                return f"{years} years {months:02d} months {days:02d} days"
            
            # If it is not found in the PID, search the content
            age_pattern = r'\*CHI:\s*.*?(\d+)[;:]'
            match = re.search(age_pattern, content)
            if match:
                years = int(match.group(1))
                months = 0
                return f"{years} years {months:02d} months {days:02d} days"
            
            # If the age is not found, return a default value
            return "0 years 00 months 00 days"
            
        except Exception as e:
            print(f"Error extracting age: {str(e)}")
            return "0 years 00 months 00 days"
    
    def extract_child_name(self, content, file_path=None):
        """Extracts the child name from the Brend file content."""
        try:
            # Special case for Brend: extract the name from the subfolder
            if file_path and 'Brent' in file_path:
                # The pattern is Brent/[a-z]\d+/ (for example, Brent/c1/, Brent/d1/, etc.)
                brend_pattern = r'Brent/([a-z]\d+)/'
                match = re.search(brend_pattern, file_path)
                if match:
                    return match.group(1)
            
            # For other cases, keep the existing logic
            # Search in the @ID line
            id_pattern = r'@ID:\s*eng\|([^|]+)\|CHI'
            id_match = re.search(id_pattern, content)
            if id_match:
                return id_match.group(1)
            
            # If it is not found in @ID, search participants
            participants_pattern = r'@Participants:\s*([^\n]+)'
            participants_match = re.search(participants_pattern, content)
            if participants_match:
                participants = participants_match.group(1)
                chi_pattern = r'CHI\s+([^,]+)'
                chi_match = re.search(chi_pattern, participants)
                if chi_match:
                    return chi_match.group(1)
                
            # If it is not found in participants, search the PID
            pid_pattern = r'@PID:\s*([^\n]+)'
            pid_match = re.search(pid_pattern, content)
            if pid_match:
                pid = pid_match.group(1)
                child_pattern = r'Child:\s*([^,]+)'
                child_match = re.search(child_pattern, pid)
                if child_match:
                    return child_match.group(1)
                
            # If it is not found anywhere, search comments
            comment_pattern = r'@Comment:\s*([^\n]+)'
            comment_match = re.search(comment_pattern, content)
            if comment_match:
                comment = comment_match.group(1)
                name_pattern = r'name:\s*([^,]+)'
                name_match = re.search(name_pattern, comment)
                if name_match:
                    return name_match.group(1)
                
            # If it is not found anywhere, use the file name
            return "Target_Child"
        except Exception as e:
            print(f"Error extracting child name: {e}")
            return "Target_Child"
    
    def add_metadata_to_content(self, content, age, child_name):
        """Adds metadata to the file content"""
        if content is None:
            return ""
        
        lines = content.split('\n')
        new_lines = []
        languages_found = False
        age_added = False
        name_added = False
        
        for line in lines:
            # If the line is age or name metadata, update it
            if line.startswith('@ChildAge:') and age:
                new_lines.append(f'@ChildAge: {age}')
                age_added = True
            elif line.startswith('@ChildName:') and child_name:
                new_lines.append(f'@ChildName: {child_name}')
                name_added = True
            else:
                new_lines.append(line)
                
            # If @Languages is found and metadata has not been added yet, add it
            if line.startswith('@Languages:') and not languages_found:
                languages_found = True
                if age and not age_added:
                    new_lines.append(f'@ChildAge: {age}')
                    age_added = True
                if child_name and not name_added:
                    new_lines.append(f'@ChildName: {child_name}')
                    name_added = True
        
        return '\n'.join(new_lines) 