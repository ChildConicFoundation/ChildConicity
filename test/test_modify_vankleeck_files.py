import unittest
import os
import shutil
import tempfile
from pathlib import Path
from src.corpus_normalizers.vankleeck_normalizer import extract_age, modify_cha_file, process_directory

class TestModifyVanKleeckFiles(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear un directorio temporal para los tests
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.test_dir, "source")
        self.target_dir = os.path.join(self.test_dir, "target")
        os.makedirs(self.source_dir)
        os.makedirs(self.target_dir)

    def tearDown(self):
        """Limpieza después de cada test"""
        # Eliminar el directorio temporal
        shutil.rmtree(self.test_dir)

    def test_extract_age(self):
        """Test para la función extract_age"""
        # Crear un archivo .cha de prueba
        test_file = os.path.join(self.source_dir, "test.cha")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('@ID:\teng|VanKleeck|CHI|3;09.|female|TD||Target_Child|||\n')
        
        # Probar la extracción de edad
        age = extract_age(test_file)
        self.assertEqual(age, "3 years 09 months 0 days")

        # Probar con un archivo que no existe
        self.assertIsNone(extract_age("no_existe.cha"))

    def test_modify_cha_file(self):
        """Test para la función modify_cha_file"""
        # Crear un archivo .cha de prueba
        test_file = os.path.join(self.source_dir, "test.cha")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('@UTF8\n@PID:\t12345\n@Begin\n@Languages:\teng\n@Participants:\tCHI Test Target_Child\n')

        # Modificar el archivo
        modify_cha_file(test_file, "test", "3 years 09 months 0 days")

        # Verificar que los metadatos se han añadido correctamente
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('@Languages:\teng', content)
            self.assertIn('@ChildName: test', content)
            self.assertIn('@ChildAge: 3 years 09 months 0 days', content)
            self.assertIn('@Participants:\tCHI Test Target_Child', content)

    def test_process_directory(self):
        """Test para la función process_directory"""
        # Crear archivos de prueba
        test_files = {
            "amy1.cha": '@UTF8\n@PID:\t12345\n@Begin\n@Languages:\teng\n@Participants:\tCHI Amy Target_Child\n@ID:\teng|VanKleeck|CHI|3;09.|female|TD||Target_Child|||\n',
            "amy2.cha": '@UTF8\n@PID:\t12345\n@Begin\n@Languages:\teng\n@Participants:\tCHI Amy Target_Child\n@ID:\teng|VanKleeck|CHI|3;09.|female|TD||Target_Child|||\n',
            "ben1.cha": '@UTF8\n@PID:\t12345\n@Begin\n@Languages:\teng\n@Participants:\tCHI Ben Target_Child\n@ID:\teng|VanKleeck|CHI|4;02.|male|TD||Target_Child|||\n'
        }

        for filename, content in test_files.items():
            with open(os.path.join(self.source_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)

        # Procesar el directorio
        process_directory(self.source_dir, self.target_dir)

        # Verificar que se han creado los directorios correctos
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "amy")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "ben")))

        # Verificar que los archivos se han copiado y modificado correctamente
        amy_file = os.path.join(self.target_dir, "amy", "amy1.cha")
        self.assertTrue(os.path.exists(amy_file))
        with open(amy_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('@Languages:\teng', content)
            self.assertIn('@ChildName: amy', content)
            self.assertIn('@ChildAge: 3 years 09 months 0 days', content)
            self.assertIn('@Participants:\tCHI Amy Target_Child', content)

    def test_process_directory_with_invalid_files(self):
        """Test para la función process_directory con archivos inválidos"""
        # Crear un archivo con formato inválido
        with open(os.path.join(self.source_dir, "invalid.cha"), 'w', encoding='utf-8') as f:
            f.write('Invalid content\n')

        # Procesar el directorio
        process_directory(self.source_dir, self.target_dir)

        # Verificar que el script no falla con archivos inválidos
        self.assertTrue(os.path.exists(self.target_dir))

if __name__ == '__main__':
    unittest.main() 