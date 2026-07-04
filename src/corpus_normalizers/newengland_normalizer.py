import os
import shutil
import re
from pathlib import Path

def extract_age(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Search for the line containing the child age
        match = re.search(r'@ID:\s*eng\|NewEngland\|CHI\|(\d+;\d+\.\d+)\|', content)
        if match:
            age_str = match.group(1)
            # Convert the 1;06.26 format to years, months, and days
            years, rest = age_str.split(';')
            months, days = rest.split('.')
            return f"{years} years {months} months {days} days"
    return None

def modify_cha_file(file_path, child_name, age):
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

    # Get all NewEngland subfolders (14, 20, 32)
    subdirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]

    # Create Target01 through Target99 directories
    for i in range(1, 100):
        target_folder = f'Target{i:02d}'  # Format: Target01, Target02, etc.
        target_folder_path = os.path.join(target_dir, target_folder)
        
        # Create the target folder if it does not exist
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)

    # For each subfolder (14, 20, 32)
    for subdir in subdirs:
        subdir_path = os.path.join(source_dir, subdir)
        
        # For each .cha file in the subfolder
        for file in os.listdir(subdir_path):
            if file.endswith('.cha'):
                # The file number without the extension indicates the Target
                target_num = int(os.path.splitext(file)[0])  # Convert to integer
                target_folder = f'Target{target_num:02d}'
                target_folder_path = os.path.join(target_dir, target_folder)
                
                # Copy the file using the subfolder name (14.cha, 20.cha, 32.cha)
                source_file = os.path.join(subdir_path, file)
                target_file = os.path.join(target_folder_path, f'{subdir}.cha')
                
                # Copy the file
                shutil.copy2(source_file, target_file)
                
                # Extract the age and modify the .cha file
                age = extract_age(source_file)
                if age:
                    modify_cha_file(target_file, target_folder, age)
                
                print(f'Copied and modified {source_file} to {target_file}')

def main():
    """Main function that runs the reorganization process."""
    # Get the project root directory path
    project_root = Path(__file__).parent.parent
    
    # Source and target directories
    source_dir = project_root / "Corpora" / "NewEngland"
    corpus_modified_dir = project_root / "Corpora_modified"
    
    # Create the Corpora_modified directory if it does not exist
    if not corpus_modified_dir.exists():
        corpus_modified_dir.mkdir()
    
    target_dir = corpus_modified_dir / "NewEngland"
    
    try:
        process_directory(str(source_dir), str(target_dir))
        print('Reorganization completed')
    except Exception as e:
        print(f'Error during reorganization: {str(e)}')
        raise

if __name__ == '__main__':
    main() 