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
    """Fixture para crear archivos de prueba temporales"""
    # Crear directorio temporal para las pruebas
    test_dir = "test_post_files"
    os.makedirs(test_dir, exist_ok=True)
    
    # Crear archivo con edad válida
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
    
    # Crear archivo sin edad
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
    
    # Crear archivo sin línea @Languages
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
    
    # Limpieza después de las pruebas
    shutil.rmtree(test_dir)

def test_extract_age():
    # Caso 1: Edad válida
    test_content = "@ID: eng|Post|CHI|1;06.26|male|TD||Target_Child|||"
    test_file = "test_age.cha"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    expected_age = "1 years 06 months 26 days"
    assert extract_age(test_file) == expected_age

    # Caso 2: Edad sin día explícito
    test_content = "@ID: eng|Post|CHI|1;06.|male|TD||Target_Child|||"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)

    expected_age = "1 years 06 months 00 days"
    assert extract_age(test_file) == expected_age
    
    # Caso 3: Archivo sin edad
    test_content = "@ID: eng|Post|CHI||male|TD||Target_Child|||"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    assert extract_age(test_file) is None
    
    # Caso 4: Archivo vacío
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
@ID: eng|Post|CHI|1;06.26|male|TD||Target_Child|||
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
    
    # Limpieza
    os.remove(test_file)

def test_modify_cha_file_without_languages():
    # Preparar archivo de prueba sin línea @Languages
    test_content = """@UTF8
@PID: test
@Begin
@Participants: INV Investigator, CHI Target_Child
@ID: eng|Post|CHI|1;06.26|male|TD||Target_Child|||
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

@pytest.fixture
def test_directory_structure(tmp_path):
    """Fixture para crear una estructura de directorios de prueba"""
    # Crear estructura de directorios temporal usando tmp_path
    test_root = tmp_path / "Post"
    test_root.mkdir()
    
    # Crear archivos de metadatos
    (test_root / "0metadata.cdc").write_text("Test metadata")
    (test_root / "0types.txt").write_text("Test types")
    
    # Crear subdirectorios y archivos .cha
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
    
    # La limpieza es automática con tmp_path

def test_process_directory(test_directory_structure, monkeypatch):
    """Prueba la función process_directory"""
    # Crear estructura de directorios de prueba
    source_dir = os.path.join(test_directory_structure, "Corpus", "Post")
    target_dir = os.path.join(test_directory_structure, "Corpus", "Post_modified")
    subdir = "test_subdir"
    source_subdir = os.path.join(source_dir, subdir)
    
    try:
        # Crear directorios
        os.makedirs(source_subdir, exist_ok=True)
        
        # Crear archivo .cha de prueba
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
        
        # Procesar directorio
        process_directory(source_dir, target_dir)
        
        # Verificar que se creó el directorio de destino
        assert os.path.exists(target_dir)
        
        # Verificar que se creó el archivo modificado
        target_file = os.path.join(target_dir, subdir, "test.cha")
        assert os.path.exists(target_file)
        
        # Verificar el contenido del archivo modificado
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "@ChildName: test_subdir" in content
        assert "@ChildAge: 1 years 06 months 26 days" in content
        
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
