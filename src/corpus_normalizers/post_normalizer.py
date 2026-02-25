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
            match = re.search(r'@ID:\s*eng\|Post\|CHI\|(\d+;\d+\.\d+)\|', content)
            if match:
                age_str = match.group(1)
                # Convertir el formato 1;06.26 a años, meses y días
                years, rest = age_str.split(';')
                months, days = rest.split('.')
                return f"{years} years {months} months {days} days"
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

    # Obtener todas las subcarpetas de Post
    subdirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]

    # Para cada subcarpeta
    for subdir in subdirs:
        subdir_path = os.path.join(source_dir, subdir)
        
        # Crear la carpeta de destino si no existe
        target_subdir = os.path.join(target_dir, subdir)
        if not os.path.exists(target_subdir):
            os.makedirs(target_subdir)
        
        # Para cada archivo .cha en la subcarpeta
        for file in os.listdir(subdir_path):
            if file.endswith('.cha'):
                # Copiar el archivo
                source_file = os.path.join(subdir_path, file)
                target_file = os.path.join(target_subdir, file)
                shutil.copy2(source_file, target_file)
                
                # Extraer la edad y modificar el archivo .cha
                age = extract_age(source_file)
                if age:
                    modify_cha_file(target_file, subdir, age)
                
                print(f'Copiado y modificado {source_file} a {target_file}')

def main():
    """Función principal que ejecuta el proceso de modificación."""
    # Obtener la ruta del directorio raíz del proyecto
    project_root = Path(__file__).parent.parent
    
    # Directorios de origen y destino
    source_dir = project_root / "Corpus" / "Post"
    corpus_modified_dir = project_root / "Corpus_modified"
    
    # Crear el directorio Corpus_modified si no existe
    if not corpus_modified_dir.exists():
        corpus_modified_dir.mkdir()
    
    target_dir = corpus_modified_dir / "Post"
    
    try:
        process_directory(str(source_dir), str(target_dir))
        print('Procesamiento completado exitosamente')
    except Exception as e:
        print(f'Error durante el procesamiento: {str(e)}')
        raise

if __name__ == '__main__':
    main() 