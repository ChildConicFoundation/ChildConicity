import unittest
import os
import shutil
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corpus_normalizers.brent_normalizer import BrendManipulator

class TestBrendManipulator(unittest.TestCase):
    def setUp(self):
        """Initial test setup"""
        self.test_dir = "test_brend"
        self.test_output_dir = "test_brend_modified"
        
        # Create test directories
        os.makedirs(self.test_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # Create a test file
        self.test_file = os.path.join(self.test_dir, "c1", "test.cha")
        os.makedirs(os.path.dirname(self.test_file), exist_ok=True)
        
        # Test content
        test_content = """@UTF8
@PID: eng|CHILDES|Brend|c1|000828|2;0|female|Target_Child|typical
@Languages: eng
@Participants: CHI c1 Target_Child, MOT Mother, FAT Father
@Options: utf8
@Media: video, audio
@Date: 2000-08-28
@Types: CHI Target_Child, MOT Mother, FAT Father
*CHI: hola mama.
%mor: hola mama
%gra: 1|1|INTJ 2|2|N
*MOT: hola cariño.
%mor: hola cariño
%gra: 1|1|INTJ 2|2|N
"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Initialize the manipulator
        self.manipulator = BrendManipulator()
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
        self.manipulator.process_file("archivo_inexistente.cha", "salida.cha")
        # It should not raise an exception, only print an error message
    
    def test_extract_age_with_error(self):
        """Test error handling in extract_age"""
        # Try extracting the age from a file that does not exist
        age = self.manipulator.extract_age("archivo_inexistente.cha")
        self.assertEqual(age, "0 years 00 months 00 days")
    
    def test_extract_child_name_from_brend_path(self):
        """Test extracting the child name from the Brend file path"""
        name = self.manipulator.extract_child_name("", self.test_file)
        self.assertEqual(name, "Target_Child")
    
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
@ChildAge: 1 years, 0 months, 0 days
@ChildName: Juan
"""
        modified = self.manipulator.add_metadata_to_content(content, "2 years, 0 months, 0 days", "Pedro")
        self.assertIn("@ChildAge: 2 years, 0 months, 0 days", modified)
        self.assertIn("@ChildName: Pedro", modified)
    
    def test_add_metadata_to_content_without_languages(self):
        """Test metadata insertion when @Languages is missing"""
        content = """@UTF8
@Participants: CHI Juan Target_Child
"""
        modified = self.manipulator.add_metadata_to_content(content, "2;0", "Pedro")
        self.assertNotIn("@Age:", modified)
        self.assertNotIn("@ChildName:", modified)
    
    def test_extract_age_from_pid(self):
        """Test extracting age from the PID"""
        age = self.manipulator.extract_age(self.test_file)
        self.assertEqual(age, "2 years 00 months 00 days")
    
    def test_extract_age_from_id(self):
        """Test extracting age from @ID"""
        test_file = os.path.join(self.test_dir, "c1", "test_id.cha")
        test_content = """@UTF8
@ID: eng|VanKleeck|CHI|3;09.|male|TD||Target_Child|||
@Languages: eng
"""
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        age = self.manipulator.extract_age(test_file)
        self.assertEqual(age, "3 years 09 months 00 days")
    
    def test_extract_age_from_content(self):
        """Test extracting age from the content"""
        test_file = os.path.join(self.test_dir, "c1", "test_content.cha")
        test_content = """@UTF8
@Languages: eng
*CHI: 2;0 hola mama.
"""
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        age = self.manipulator.extract_age(test_file)
        self.assertEqual(age, "2 years 00 months 00 days")
    
    def test_process_directory(self):
        """Test full directory processing"""
        self.manipulator.process_directory()
        
        # Check that the output file exists and contains the metadata
        output_file = os.path.join(self.test_output_dir, "c1", "test.cha")
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn("@ChildAge: 2 years 00 months 00 days", content)
        self.assertIn("@ChildName: c1", content)
    
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
        self.manipulator.process_file(self.test_file, "salida.cha")
        self.assertTrue(os.path.exists("salida.cha"))
        os.remove("salida.cha") 