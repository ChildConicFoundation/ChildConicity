import os
import pytest
import shutil
from src.corpus_normalizers.post_normalizer import (
    extract_age,
    modify_cha_file,
    process_directory,
)

@pytest.fixture
def test_files():
    """Fixture for creating temporary test files"""
    # Create a temporary directory for tests
    test_dir = "test_post_files"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a file with a valid age
    valid_age_content = """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: CHI Target_Child
@ID: eng|Post|CHI|1;06.26|male|TD||Target_Child|||
"""
    valid_file = os.path.join(test_dir, "valid_age.cha")
    with open(valid_file, 'w', encoding='utf-8') as f:
        f.write(valid_age_content)
    
    # Create a file without an age
    no_age_content = """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: CHI Target_Child
@ID: eng|Post|CHI||male|TD||Target_Child|||
"""
    no_age_file = os.path.join(test_dir, "no_age.cha")
    with open(no_age_file, 'w', encoding='utf-8') as f:
        f.write(no_age_content)
    
    # Create a file without an @Languages line
    no_lang_content = """@UTF8
@PID: test
@Begin
@Participants: CHI Target_Child
@ID: eng|Post|CHI|1;06.26|male|TD||Target_Child|||
"""
    no_lang_file = os.path.join(test_dir, "no_lang.cha")
    with open(no_lang_file, 'w', encoding='utf-8') as f:
        f.write(no_lang_content)
    
    yield {
        'valid_file': valid_file,
        'no_age_file': no_age_file,
        'no_lang_file': no_lang_file,
        'test_dir': test_dir
    }
    
    # Cleanup after the tests
    shutil.rmtree(test_dir)

def test_extract_age():
    # Case 1: Valid age
    test_content = "@ID: eng|Post|CHI|1;06.26|male|TD||Target_Child|||"
    test_file = "test_age.cha"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    expected_age = "1 years 06 months 26 days"
    assert extract_age(test_file) == expected_age

    # Case 2: Age without explicit day
    test_content = "@ID: eng|Post|CHI|1;06.|male|TD||Target_Child|||"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)

    expected_age = "1 years 06 months 00 days"
    assert extract_age(test_file) == expected_age
    
    # Case 3: File without an age
    test_content = "@ID: eng|Post|CHI||male|TD||Target_Child|||"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    assert extract_age(test_file) is None
    
    # Case 4: Empty file
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
@ID: eng|Post|CHI|1;06.26|male|TD||Target_Child|||
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
    
    expected_content = """@UTF8
@PID: test
@Begin
@Languages: eng
@ChildName: Target01
@ChildAge: 1 years 06 months 26 days
@Participants: INV Investigator, CHI Target_Child
@ID: eng|Post|CHI|1;06.26|male|TD||Target_Child|||
"""
    assert content == expected_content
    
    # Cleanup
    os.remove(test_file)

def test_modify_cha_file_without_languages():
    # Prepare test file without an @Languages line
    test_content = """@UTF8
@PID: test
@Begin
@Participants: INV Investigator, CHI Target_Child
@ID: eng|Post|CHI|1;06.26|male|TD||Target_Child|||
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

@pytest.fixture
def test_directory_structure(tmp_path):
    """Fixture for creating a test directory structure"""
    # Create temporary directory structure using tmp_path
    test_root = tmp_path / "Post"
    test_root.mkdir()
    
    # Create metadata files
    (test_root / "0metadata.cdc").write_text("Test metadata")
    (test_root / "0types.txt").write_text("Test types")
    
    # Create subdirectories and .cha files
    subdirs = ["Lew", "She", "Tow"]
    for subdir in subdirs:
        subdir_path = test_root / subdir
        subdir_path.mkdir()
        (subdir_path / "test.cha").write_text("""@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: CHI Target_Child
@ID: eng|Post|CHI|1;06.26|male|TD||Target_Child|||
""")
    
    yield tmp_path
    
    # Cleanup is automatic with tmp_path

def test_process_directory(test_directory_structure, monkeypatch):
    """Test the process_directory function"""
    # Create test directory structure
    source_dir = os.path.join(test_directory_structure, "Corpus", "Post")
    target_dir = os.path.join(test_directory_structure, "Corpus", "Post_modified")
    subdir = "test_subdir"
    source_subdir = os.path.join(source_dir, subdir)
    
    try:
        # Create directories
        os.makedirs(source_subdir, exist_ok=True)
        
        # Create a test .cha file
        test_file = os.path.join(source_subdir, "test.cha")
        test_content = """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: INV Investigator, CHI Target_Child
@ID: eng|Post|CHI|1;06.26|male|TD||Target_Child|||
"""
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Process directory
        process_directory(source_dir, target_dir)
        
        # Check that the target directory was created
        assert os.path.exists(target_dir)
        
        # Check that the modified file was created
        target_file = os.path.join(target_dir, subdir, "test.cha")
        assert os.path.exists(target_file)
        
        # Check the modified file content
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "@ChildName: test_subdir" in content
        assert "@ChildAge: 1 years 06 months 26 days" in content
        
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
