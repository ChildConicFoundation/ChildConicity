import os
import pytest
from src.corpus_normalizers.newengland_normalizer import extract_age, modify_cha_file, process_directory

def test_extract_age():
    # Case 1: Valid age
    test_content = "@ID: eng|NewEngland|CHI|1;06.26|male|TD||Target_Child|||"
    test_file = "test_age.cha"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    expected_age = "1 years 06 months 26 days"
    assert extract_age(test_file) == expected_age
    
    # Case 2: File without an age
    test_content = "@ID: eng|NewEngland|CHI||male|TD||Target_Child|||"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    assert extract_age(test_file) is None
    
    # Case 3: Empty file
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("")
    
    assert extract_age(test_file) is None
    
    # Cleanup
    os.remove(test_file)

def test_modify_cha_file():
    # Prepare test file
    test_content = """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: INV Investigator, CHI Target_Child
@ID: eng|NewEngland|CHI|1;06.26|male|TD||Target_Child|||
"""
    test_file = "test_modify.cha"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Test the modification
    child_name = "Target01"
    age = "1 years 06 months 26 days"
    modify_cha_file(test_file, child_name, age)
    
    # Check the result
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert "@ChildAge: 1 years 06 months 26 days" in content
    assert "@ChildName: Target01" in content
    
    # Cleanup
    os.remove(test_file)

def test_modify_cha_file_without_languages():
    # Prepare test file without an @Languages line
    test_content = """@UTF8
@PID: test
@Begin
@Participants: INV Investigator, CHI Target_Child
@ID: eng|NewEngland|CHI|1;06.26|male|TD||Target_Child|||
"""
    test_file = "test_modify_no_lang.cha"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Test the modification
    child_name = "Target01"
    age = "1 years 06 months 26 days"
    modify_cha_file(test_file, child_name, age)
    
    # Check the result
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The file should remain unchanged because there is no @Languages line
    assert content == test_content
    
    # Cleanup
    os.remove(test_file)

def test_process_directory():
    # Create test directory structure
    source_dir = "test_source"
    target_dir = "test_target"
    subdir = "14"  # Use a valid subdirectory (14, 20, or 32)
    source_subdir = os.path.join(source_dir, subdir)
    
    try:
        # Create directories
        os.makedirs(source_subdir, exist_ok=True)
        
        # Create a test .cha file with a number as its name
        test_file = os.path.join(source_subdir, "01.cha")  # Use a number as the file name
        test_content = """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: INV Investigator, CHI Target_Child
@ID: eng|NewEngland|CHI|1;06.26|male|TD||Target_Child|||
"""
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Process directory
        process_directory(source_dir, target_dir)
        
        # Check that the target directory was created
        assert os.path.exists(target_dir)
        
        # Check that the modified file was created in Target01
        target_file = os.path.join(target_dir, "Target01", "14.cha")
        assert os.path.exists(target_file)
        
        # Check the modified file content
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "@ChildAge: 1 years 06 months 26 days" in content
        assert "@ChildName: Target01" in content
        
    finally:
        # Cleanup
        if os.path.exists(target_dir):
            for root, dirs, files in os.walk(target_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(target_dir)
        
        if os.path.exists(source_dir):
            for root, dirs, files in os.walk(source_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(source_dir) 