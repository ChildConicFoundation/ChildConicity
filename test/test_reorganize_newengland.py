import os
import pytest
from src.corpus_normalizers.newengland_normalizer import extract_age, modify_cha_file, process_directory

def test_extract_age():
    # Caso 1: Edad válida
    test_content = "@ID: eng|NewEngland|CHI|1;06.26|male|TD||Target_Child|||"
    test_file = "test_age.cha"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    expected_age = "1 years 06 months 26 days"
    assert extract_age(test_file) == expected_age
    
    # Caso 2: Archivo sin edad
    test_content = "@ID: eng|NewEngland|CHI||male|TD||Target_Child|||"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    assert extract_age(test_file) is None
    
    # Caso 3: Archivo vacío
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("")
    
    assert extract_age(test_file) is None
    
    # Limpieza
    os.remove(test_file)

def test_modify_cha_file():
    # Preparar archivo de prueba
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
    
    # Probar la modificación
    child_name = "Target01"
    age = "1 years 06 months 26 days"
    modify_cha_file(test_file, child_name, age)
    
    # Verificar el resultado
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert "@ChildAge: 1 years 06 months 26 days" in content
    assert "@ChildName: Target01" in content
    
    # Limpieza
    os.remove(test_file)

def test_modify_cha_file_without_languages():
    # Preparar archivo de prueba sin línea @Languages
    test_content = """@UTF8
@PID: test
@Begin
@Participants: INV Investigator, CHI Target_Child
@ID: eng|NewEngland|CHI|1;06.26|male|TD||Target_Child|||
"""
    test_file = "test_modify_no_lang.cha"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Probar la modificación
    child_name = "Target01"
    age = "1 years 06 months 26 days"
    modify_cha_file(test_file, child_name, age)
    
    # Verificar el resultado
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # El archivo debería permanecer sin cambios ya que no hay línea @Languages
    assert content == test_content
    
    # Limpieza
    os.remove(test_file)

def test_process_directory():
    # Crear estructura de directorios de prueba
    source_dir = "test_source"
    target_dir = "test_target"
    subdir = "14"  # Usamos un subdirectorio válido (14, 20, o 32)
    source_subdir = os.path.join(source_dir, subdir)
    
    try:
        # Crear directorios
        os.makedirs(source_subdir, exist_ok=True)
        
        # Crear archivo .cha de prueba con un número como nombre
        test_file = os.path.join(source_subdir, "01.cha")  # Usamos un número como nombre de archivo
        test_content = """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: INV Investigator, CHI Target_Child
@ID: eng|NewEngland|CHI|1;06.26|male|TD||Target_Child|||
"""
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Procesar directorio
        process_directory(source_dir, target_dir)
        
        # Verificar que se creó el directorio de destino
        assert os.path.exists(target_dir)
        
        # Verificar que se creó el archivo modificado en Target01
        target_file = os.path.join(target_dir, "Target01", "14.cha")
        assert os.path.exists(target_file)
        
        # Verificar el contenido del archivo modificado
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "@ChildAge: 1 years 06 months 26 days" in content
        assert "@ChildName: Target01" in content
        
    finally:
        # Limpieza
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