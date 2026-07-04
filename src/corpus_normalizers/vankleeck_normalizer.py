import os
import shutil
import re
from pathlib import Path

def extract_age(file_path):
    """Extracts the age from the file .cha"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Search for the line containing the child age
            # The format is |3;09.| where 3 is years, 09 is months, and there are no days
            match = re.search(r'@ID:\s*eng\|VanKleeck\|CHI\|(\d+);(\d+)\.\|', content)
            if match:
                years = match.group(1)
                months = match.group(2)
                # Assume days = 0 because it is not specified
                return f"{years} years {months} months 0 days"
    except FileNotFoundError:
        return None
    return None

def modify_cha_file(file_path, child_name, age):
    """Modifies the .cha file to add metadata"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the position after @Languages
    languages_pos = content.find('@Languages:')
    if languages_pos != -1:
        # Find the end of the @Languages line
        end_of_line = content.find('\n', languages_pos)
        if end_of_line != -1:
            # Insert metadata after @Languages
            new_content = content[:end_of_line + 1] + f'@ChildName: {child_name}\n@ChildAge: {age}\n' + content[end_of_line + 1:]
            
            # Write the modified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

def process_directory(source_dir, target_dir):
    """Processes .cha files from the source directory and copies them to the target directory."""
    # Create the target directory if it does not exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Get all .cha files
    cha_files = [f for f in os.listdir(source_dir) if f.endswith('.cha')]
    
    # Group files by child name, removing the number and extra trailing letters
    child_files = {}
    for file in cha_files:
        # Extract the base name (for example, 'justin' from 'justin1a.cha')
        match = re.match(r'([a-zA-Z]+)(?:\d+[a-z]*)?\.cha', file)
        if match:
            child_name = match.group(1).lower()
            if child_name not in child_files:
                child_files[child_name] = []
            child_files[child_name].append(file)
    
    # Process each file group
    for child_name, files in child_files.items():
        # Create the child directory
        child_dir = os.path.join(target_dir, child_name)
        if not os.path.exists(child_dir):
            os.makedirs(child_dir)
        
        # Copy and modify each file
        for file in files:
            source_file = os.path.join(source_dir, file)
            target_file = os.path.join(child_dir, file)
            shutil.copy2(source_file, target_file)
            
            # Extract the age and modify the .cha file
            age = extract_age(source_file)
            if age:
                modify_cha_file(target_file, child_name, age)
            
            print(f'Copied and modified {source_file} to {target_file}')

def main():
    """Main function that runs the modification process."""
    # Get the project root directory path
    project_root = Path(__file__).parent.parent
    
    # Source and target directories
    source_dir = project_root / "Corpora" / "VanKleeck"
    corpus_modified_dir = project_root / "Corpora_modified"
    
    # Create the Corpora_modified directory if it does not exist
    if not corpus_modified_dir.exists():
        corpus_modified_dir.mkdir()
    
    target_dir = corpus_modified_dir / "VanKleeck"
    
    try:
        process_directory(str(source_dir), str(target_dir))
        print('Processing completed successfully')
    except Exception as e:
        print(f'Error during processing: {str(e)}')
        raise

if __name__ == '__main__':
    main() 