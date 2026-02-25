import os
import re
from src.data_io.data_formatter import DataFormatter

class CorpusManipulator:
    """Manipulador genérico para todos los corpus"""
    
    def __init__(self):
        self.base_dir = None
        self.output_dir = None
        self.formatter = DataFormatter()
    
    def process_directory(self):
        """Procesa el directorio del corpus"""
        if not self.base_dir:
            raise ValueError("base_dir no está configurado")
            
        # Procesar todos los archivos .cha en el directorio
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith('.cha'):
                    file_path = os.path.join(root, file)
                    # Crear la estructura de directorios en el output_dir
                    if self.output_dir:
                        rel_path = os.path.relpath(root, self.base_dir)
                        output_root = os.path.join(self.output_dir, rel_path)
                        os.makedirs(output_root, exist_ok=True)
                        output_path = os.path.join(output_root, file)
                    else:
                        output_path = file_path
                    
                    # Procesar el archivo
                    self.process_file(file_path, output_path)
    
    def process_file(self, input_path, output_path):
        """Procesa un archivo .cha individual"""
        # Extraer la edad del archivo
        age = self.extract_age(input_path)
        
        try:
            # Leer el contenido del archivo
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer el nombre del niño pasando también la ruta del archivo
            child_name = self.extract_child_name(content, input_path)
            
            # Modificar el archivo con la edad extraída y el nombre
            modified_content = self.add_metadata_to_content(content, age, child_name)
            
            # Guardar el archivo modificado
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
                
            print(f"Archivo modificado exitosamente: {output_path}")
        except Exception as e:
            print(f"Error al procesar el archivo {input_path}: {str(e)}")
    
    def extract_age(self, file_path):
        """Extrae la edad del archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Caso especial para Brent: extraer la edad del nombre del archivo
            if 'Brent' in file_path:
                file_name = os.path.basename(file_path)
                if file_name.endswith('.cha'):
                    file_name = file_name[:-4]  # Quitar la extensión .cha
                    if len(file_name) >= 6:  # Asegurarse de que tiene al menos 6 dígitos
                        years = int(file_name[0:2])
                        months = int(file_name[2:4])
                        days = int(file_name[4:6])
                        return f"{years};{months}"
            
            # Buscar la edad en el PID
            pid_pattern = r'@PID:.*?\|(\d+);(\d+)\|'
            match = re.search(pid_pattern, content)
            if match:
                years = int(match.group(1))
                months = int(match.group(2))
                return f"{years};{months}"
                
            # Buscar la edad en el formato @ID: eng|VanKleeck|CHI|3;08.|male|TD||Target_Child|||
            id_pattern = r'@ID:.*?CHI\|(\d+);(\d+)\.'
            match = re.search(id_pattern, content)
            if match:
                years = int(match.group(1))
                months = int(match.group(2))
                return f"{years};{months}"
                
            # Si no se encuentra en el PID, buscar en el contenido
            age_pattern = r'\*CHI:\s*.*?(\d+)[;:]'
            match = re.search(age_pattern, content)
            if match:
                years = int(match.group(1))
                return f"{years};0"
                
            return None
        except Exception as e:
            print(f"Error al extraer la edad de {file_path}: {str(e)}")
            return None
    
    def modify_file(self, input_path, output_path, age):
        """Modifica el archivo con la edad extraída"""
        if age is None:
            return
            
        try:
            # Leer el contenido del archivo
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer el nombre del niño pasando también la ruta del archivo
            child_name = self.extract_child_name(content, input_path)
            
            # Modificar el contenido con la edad y el nombre
            modified_content = self.add_metadata_to_content(content, age, child_name)
            
            # Guardar el archivo modificado
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
                
            print(f"Archivo modificado exitosamente: {output_path}")
        except Exception as e:
            print(f"Error al modificar el archivo {input_path}: {str(e)}")
    
    def extract_child_name(self, content, file_path=None):
        """Extrae el nombre del niño del contenido del archivo."""
        try:
            # Caso especial para Brent: extraer el nombre de la subcarpeta
            if file_path and 'Brent' in file_path:
                # El patrón será Brent/[a-z]\d+/ (por ejemplo, Brent/c1/, Brent/d1/, etc.)
                brent_pattern = r'Brent/([a-z]\d+)/'
                match = re.search(brent_pattern, file_path)
                if match:
                    return match.group(1)
            
            # Para otros casos, seguir con la lógica existente
            # Buscar en la línea @ID
            id_pattern = r'@ID:\s*eng\|([^|]+)\|CHI'
            id_match = re.search(id_pattern, content)
            if id_match:
                return id_match.group(1)
            
            # Si no se encuentra en @ID, buscar en los participantes
            participants_pattern = r'@Participants:\s*([^\n]+)'
            participants_match = re.search(participants_pattern, content)
            if participants_match:
                participants = participants_match.group(1)
                chi_pattern = r'CHI\s+([^,]+)'
                chi_match = re.search(chi_pattern, participants)
                if chi_match:
                    return chi_match.group(1)
                
            # Si no se encuentra en los participantes, buscar en el PID
            pid_pattern = r'@PID:\s*([^\n]+)'
            pid_match = re.search(pid_pattern, content)
            if pid_match:
                pid = pid_match.group(1)
                child_pattern = r'Child:\s*([^,]+)'
                child_match = re.search(child_pattern, pid)
                if child_match:
                    return child_match.group(1)
                
            # Si no se encuentra en ninguna parte, buscar en los comentarios
            comment_pattern = r'@Comment:\s*([^\n]+)'
            comment_match = re.search(comment_pattern, content)
            if comment_match:
                comment = comment_match.group(1)
                name_pattern = r'name:\s*([^,]+)'
                name_match = re.search(name_pattern, comment)
                if name_match:
                    return name_match.group(1)
                
            # Si no se encuentra en ninguna parte, usar el nombre del archivo
            return "Target_Child"
        except Exception as e:
            print(f"Error al extraer el nombre del niño: {e}")
            return "Target_Child"
    
    def add_metadata_to_content(self, content, age, child_name):
        """Añade los metadatos al contenido del archivo"""
        if content is None:
            return ""
        
        lines = content.split('\n')
        new_lines = []
        languages_found = False
        age_added = False
        name_added = False
        
        for line in lines:
            # Si la línea es un metadato de edad o nombre, la actualizamos
            if line.startswith('@Age:') and age:
                new_lines.append(f'@Age: {age}')
                age_added = True
            elif line.startswith('@ChildName:') and child_name:
                new_lines.append(f'@ChildName: {child_name}')
                name_added = True
            else:
                new_lines.append(line)
                
            # Si encontramos @Languages y aún no hemos añadido los metadatos, los añadimos
            if line.startswith('@Languages:') and not languages_found:
                languages_found = True
                if age and not age_added:
                    new_lines.append(f'@Age: {age}')
                    age_added = True
                if child_name and not name_added:
                    new_lines.append(f'@ChildName: {child_name}')
                    name_added = True
        
        return '\n'.join(new_lines) 