import os
import shutil
import re
from pathlib import Path

def extract_age(file_path):
    """Extrae la edad del archivo .cha"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Buscar la línea que contiene la edad del niño
            # El formato es |3;09.| donde 3 son años, 09 son meses, y no hay días
            match = re.search(r'@ID:\s*eng\|VanKleeck\|CHI\|(\d+);(\d+)\.\|', content)
            if match:
                years = match.group(1)
                months = match.group(2)
                # Asumimos días = 0 ya que no viene especificado
                return f"{years} years {months} months 0 days"
    except FileNotFoundError:
        return None
    return None

def modify_cha_file(file_path, child_name, age):
    """Modifica el archivo .cha para añadir los metadatos"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la posición después de @Languages
    languages_pos = content.find('@Languages:')
    if languages_pos != -1:
        # Encontrar el final de la línea @Languages
        end_of_line = content.find('\n', languages_pos)
        if end_of_line != -1:
            # Insertar los metadatos después de @Languages
            new_content = content[:end_of_line + 1] + f'@ChildName: {child_name}\n@ChildAge: {age}\n' + content[end_of_line + 1:]
            
            # Escribir el contenido modificado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

def process_directory(source_dir, target_dir):
    """Procesa los archivos .cha del directorio de origen y los copia al directorio de destino."""
    # Crear el directorio de destino si no existe
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Obtener todos los archivos .cha
    cha_files = [f for f in os.listdir(source_dir) if f.endswith('.cha')]
    
    # Agrupar archivos por nombre de niño (eliminando el número y letras adicionales al final)
    child_files = {}
    for file in cha_files:
        # Extraer el nombre base (por ejemplo, 'justin' de 'justin1a.cha')
        match = re.match(r'([a-zA-Z]+)(?:\d+[a-z]*)?\.cha', file)
        if match:
            child_name = match.group(1).lower()
            if child_name not in child_files:
                child_files[child_name] = []
            child_files[child_name].append(file)
    
    # Procesar cada grupo de archivos
    for child_name, files in child_files.items():
        # Crear el directorio para el niño
        child_dir = os.path.join(target_dir, child_name)
        if not os.path.exists(child_dir):
            os.makedirs(child_dir)
        
        # Copiar y modificar cada archivo
        for file in files:
            source_file = os.path.join(source_dir, file)
            target_file = os.path.join(child_dir, file)
            shutil.copy2(source_file, target_file)
            
            # Extraer la edad y modificar el archivo .cha
            age = extract_age(source_file)
            if age:
                modify_cha_file(target_file, child_name, age)
            
            print(f'Copiado y modificado {source_file} a {target_file}')

def main():
    """Función principal que ejecuta el proceso de modificación."""
    # Obtener la ruta del directorio raíz del proyecto
    project_root = Path(__file__).parent.parent
    
    # Directorios de origen y destino
    source_dir = project_root / "Corpus" / "VanKleeck"
    corpus_modified_dir = project_root / "Corpus_modified"
    
    # Crear el directorio Corpus_modified si no existe
    if not corpus_modified_dir.exists():
        corpus_modified_dir.mkdir()
    
    target_dir = corpus_modified_dir / "VanKleeck"
    
    try:
        process_directory(str(source_dir), str(target_dir))
        print('Procesamiento completado exitosamente')
    except Exception as e:
        print(f'Error durante el procesamiento: {str(e)}')
        raise

if __name__ == '__main__':
    main() 