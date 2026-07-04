import unittest
import os
import shutil
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corpus_normalizers.base_normalizer import CorpusManipulator

class TestCorpusManipulator(unittest.TestCase):
    def setUp(self):
        """Initial test setup"""
        self.test_dir = "test_corpus"
        self.test_output_dir = "test_corpus_modified"
        
        # Create test directories
        os.makedirs(self.test_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # Create a test file
        self.test_file = os.path.join(self.test_dir, "test_child", "000828.cha")
        os.makedirs(os.path.dirname(self.test_file), exist_ok=True)
        
        # Test content
        test_content = """@UTF8
@PID: eng|CHILDES|Post|Lew|000828|2;0|female|Target_Child|typical
@Languages: eng
@Participants: CHI Lew Target_Child, MOT Mother, FAT Father
@Options: utf8
@Media: video, audio
@Date: 2000-08-28
@Types: CHI Target_Child, MOT Mother, FAT Father
*CHI: hello mom.
%mor: hello mom
%gra: 1|1|INTJ 2|2|N
*MOT: hello dear.
%mor: hello dear
%gra: 1|1|INTJ 2|2|N
"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Initialize the manipulator
        self.manipulator = CorpusManipulator()
        self.manipulator.base_dir = self.test_dir
        self.manipulator.output_dir = self.test_output_dir
    
    def tearDown(self):
        """Cleanup after the tests"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
    
    def test_process_directory_without_base_dir(self):
        """Test that process_directory raises an error when base_dir is not configured"""
        self.manipulator.base_dir = None
        with self.assertRaises(ValueError):
            self.manipulator.process_directory()
    
    def test_process_file_with_error(self):
        """Test error handling in process_file"""
        # Try processing a file that does not exist
        self.manipulator.process_file("nonexistent.cha", "output.cha")
        # It should not raise an exception, only print an error message
    
    def test_extract_age_with_error(self):
        """Test error handling in extract_age"""
        # Try extracting the age from a file that does not exist
        age = self.manipulator.extract_age("nonexistent.cha")
        self.assertIsNone(age)
    
    def test_modify_file_with_none_age(self):
        """Test that modify_file does nothing when age is None"""
        self.manipulator.modify_file(self.test_file, "output.cha", None)
        self.assertFalse(os.path.exists("output.cha"))
    
    def test_extract_child_name_from_participants(self):
        """Test extracting the child name from @Participants"""
        content = """@UTF8
@Languages: eng
@Participants: CHI Juan Target_Child, MOT Mother
"""
        name = self.manipulator.extract_child_name(content)
        self.assertEqual(name, "Juan Target_Child")
    
    def test_extract_child_name_from_pid(self):
        """Test extracting the child name from @PID"""
        content = """@UTF8
@Languages: eng
@PID: Child: Maria, Mother: Ana
"""
        name = self.manipulator.extract_child_name(content)
        self.assertEqual(name, "Maria")
    
    def test_extract_child_name_from_comment(self):
        """Test extracting the child name from @Comment"""
        content = """@UTF8
@Languages: eng
@Comment: name: Pedro, age: 2
"""
        name = self.manipulator.extract_child_name(content)
        self.assertEqual(name, "Pedro")
    
    def test_extract_child_name_default(self):
        """Test that Target_Child is returned when the name is not found"""
        content = """@UTF8
@Languages: eng
"""
        name = self.manipulator.extract_child_name(content)
        self.assertEqual(name, "Target_Child")
    
    def test_add_metadata_to_content_with_existing_metadata(self):
        """Test metadata insertion when metadata already exists"""
        content = """@UTF8
@Languages: eng
@Age: 1;0
@ChildName: Juan
"""
        modified = self.manipulator.add_metadata_to_content(content, "2;0", "Pedro")
        self.assertIn("@Age: 2;0", modified)
        self.assertIn("@ChildName: Pedro", modified)
    
    def test_add_metadata_to_content_without_languages(self):
        """Test metadata insertion when @Languages is missing"""
        content = """@UTF8
@Participants: CHI Juan Target_Child
"""
        modified = self.manipulator.add_metadata_to_content(content, "2;0", "Pedro")
        self.assertNotIn("@Age:", modified)
        self.assertNotIn("@ChildName:", modified)
    
    def test_calculate_age_from_filename(self):
        """Test age calculation from the file name"""
        # Test AAMMDD format
        age = self.manipulator.extract_age(self.test_file)
        self.assertEqual(age, "2;0")
        
        # Test x1-[r|f]DDmmmYY format
        test_file2 = os.path.join(self.test_dir, "test_child", "x1-r15jan00.cha")
        test_content2 = """@UTF8
@PID: eng|CHILDES|Post|Lew|x1-r15jan00|1;6|female|Target_Child|typical
@Languages: eng
*CHI: hola mama."""
        with open(test_file2, 'w', encoding='utf-8') as f:
            f.write(test_content2)
        age = self.manipulator.extract_age(test_file2)
        self.assertEqual(age, "1;6")
    
    def test_insert_age_metadata(self):
        """Test inserting age and name metadata"""
        input_path = self.test_file
        output_path = os.path.join(self.test_output_dir, "test_child", "000828.cha")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        age = self.manipulator.extract_age(input_path)
        self.manipulator.modify_file(input_path, output_path, age)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn("@Age: 2;0", content)
        self.assertIn("@ChildName: Lew", content)
    
    def test_process_directory(self):
        """Test full directory processing"""
        self.manipulator.process_directory()
        
        # Check that the output file exists and contains the metadata
        output_file = os.path.join(self.test_output_dir, "test_child", "000828.cha")
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn("@Age: 2;0", content)
        self.assertIn("@ChildName: Lew", content)

    def test_extract_child_name_with_error(self):
        """Test error handling in extract_child_name"""
        # Pass invalid content to force an exception
        name = self.manipulator.extract_child_name(None)
        self.assertEqual(name, "Target_Child")

    def test_add_metadata_to_content_with_error(self):
        """Test error handling in add_metadata_to_content"""
        # Pass invalid content to force an exception
        modified = self.manipulator.add_metadata_to_content(None, "2;0", "Pedro")
        self.assertEqual(modified, "")

    def test_process_file_with_output_dir_none(self):
        """Test process_file when output_dir is None"""
        self.manipulator.output_dir = None
        self.manipulator.process_file(self.test_file, "output.cha")
        self.assertTrue(os.path.exists("output.cha"))
        os.remove("output.cha")

    def test_extract_age_from_content(self):
        """Test extracting age from the content"""
        content = """@UTF8
@Languages: eng
*CHI: 2;0 hola mama.
"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        age = self.manipulator.extract_age(self.test_file)
        self.assertEqual(age, "2;0")

if __name__ == '__main__':
    unittest.main() 