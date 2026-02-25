import os
import shutil
import re
from pathlib import Path

def extract_age(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Buscar la línea que contiene la edad del niño
        match = re.search(r'@ID:\s*eng\|NewEngland\|CHI\|(\d+;\d+\.\d+)\|', content)
        if match:
            age_str = match.group(1)
            # Convertir el formato 1;06.26 a años, meses y días
            years, rest = age_str.split(';')
            months, days = rest.split('.')
            return f"{years} years {months} months {days} days"
    return None

def modify_cha_file(file_path, child_name, age):
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

    # Obtener todas las subcarpetas de NewEngland (14, 20, 32)
    subdirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]

    # Crear directorios Target01 a Target99
    for i in range(1, 100):
        target_folder = f'Target{i:02d}'  # Formato: Target01, Target02, etc.
        target_folder_path = os.path.join(target_dir, target_folder)
        
        # Crear la carpeta de destino si no existe
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)

    # Para cada subcarpeta (14, 20, 32)
    for subdir in subdirs:
        subdir_path = os.path.join(source_dir, subdir)
        
        # Para cada archivo .cha en la subcarpeta
        for file in os.listdir(subdir_path):
            if file.endswith('.cha'):
                # El número del archivo (sin la extensión) indica el Target
                target_num = int(os.path.splitext(file)[0])  # Convertir a entero
                target_folder = f'Target{target_num:02d}'
                target_folder_path = os.path.join(target_dir, target_folder)
                
                # Copiar el archivo con el nombre de la subcarpeta (14.cha, 20.cha, 32.cha)
                source_file = os.path.join(subdir_path, file)
                target_file = os.path.join(target_folder_path, f'{subdir}.cha')
                
                # Copiar el archivo
                shutil.copy2(source_file, target_file)
                
                # Extraer la edad y modificar el archivo .cha
                age = extract_age(source_file)
                if age:
                    modify_cha_file(target_file, target_folder, age)
                
                print(f'Copiado y modificado {source_file} a {target_file}')

def main():
    """Función principal que ejecuta el proceso de reorganización."""
    # Obtener la ruta del directorio raíz del proyecto
    project_root = Path(__file__).parent.parent
    
    # Directorios de origen y destino
    source_dir = project_root / "Corpus" / "NewEngland"
    corpus_modified_dir = project_root / "Corpus_modified"
    
    # Crear el directorio Corpus_modified si no existe
    if not corpus_modified_dir.exists():
        corpus_modified_dir.mkdir()
    
    target_dir = corpus_modified_dir / "NewEngland"
    
    try:
        process_directory(str(source_dir), str(target_dir))
        print('Reorganización completada')
    except Exception as e:
        print(f'Error durante la reorganización: {str(e)}')
        raise

if __name__ == '__main__':
    main() 