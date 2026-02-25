import os
import re
from src.data_io.data_formatter import DataFormatter

class BrendManipulator:
    """Manipulador específico para el corpus de Brend"""
    
    def __init__(self):
        self.base_dir = None
        self.output_dir = None
        self.formatter = DataFormatter()
    
    def process_directory(self):
        """Procesa el directorio del corpus de Brend"""
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
        """Procesa un archivo .cha individual del corpus de Brend"""
        try:
            # Leer el contenido del archivo
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer la edad y el nombre del niño
            age = self.extract_age(content, input_path)
            child_name = self.extract_child_name(content, input_path)
            
            # Modificar el archivo con la edad extraída y el nombre
            modified_content = self.add_metadata_to_content(content, age, child_name)
            
            # Guardar el archivo modificado
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
                
            print(f"Archivo modificado exitosamente: {output_path}")
        except Exception as e:
            print(f"Error al procesar el archivo {input_path}: {str(e)}")
    
    def extract_age(self, content, file_path=None):
        """Extrae la edad del contenido del archivo y la formatea como 'X years YY months ZZ days'"""
        try:
            years = 0
            months = 0
            days = 0
            
            # Si el contenido es una ruta de archivo, leer el archivo
            if os.path.isfile(content):
                with open(content, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Caso especial para Brent: extraer la edad del nombre del archivo
            if file_path and 'Brent' in file_path:
                # El nombre del archivo tiene el formato YYMMDD.cha o m1-[r|f]DDmmmYY.cha
                file_name = os.path.basename(file_path)
                if file_name.endswith('.cha'):
                    file_name = file_name[:-4]  # Quitar la extensión .cha
                    
                    # Caso especial para archivos m1
                    if file_name.startswith('m1-'):
                        # Formato: m1-[r|f]DDmmmYY
                        # Ejemplo: m1-r27jul00
                        match = re.match(r'm1-[rf](\d{2})([a-z]{3})(\d{2})', file_name)
                        if match:
                            day = int(match.group(1))
                            month_str = match.group(2).lower()
                            year = int(match.group(3))
                            
                            # Convertir el mes de texto a número
                            month_map = {
                                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                                'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                                'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                            }
                            month = month_map.get(month_str, 0)
                            
                            # Ajustar el año (00 -> 2000)
                            year = 2000 + year if year < 100 else year
                            
                            return f"0 years {month:02d} months {day:02d} days"
                    
                    # Caso normal: YYMMDD.cha
                    elif len(file_name) >= 6:  # Asegurarse de que tiene al menos 6 dígitos
                        years = int(file_name[0:2])
                        months = int(file_name[2:4])
                        days = int(file_name[4:6])
                        return f"{years} years {months:02d} months {days:02d} days"
            
            # Para otros casos, buscar en el contenido
            # Buscar la edad en el PID
            pid_pattern = r'@PID:.*?\|(\d+);(\d+)\|'
            match = re.search(pid_pattern, content)
            if match:
                years = int(match.group(1))
                months = int(match.group(2))
                return f"{years} years {months:02d} months {days:02d} days"
            
            # Buscar la edad en el formato @ID: eng|VanKleeck|CHI|3;09.|male|TD||Target_Child|||
            id_pattern = r'@ID:.*?CHI\|(\d+);(\d+)\.'
            match = re.search(id_pattern, content)
            if match:
                years = int(match.group(1))
                months = int(match.group(2))
                return f"{years} years {months:02d} months {days:02d} days"
            
            # Si no se encuentra en el PID, buscar en el contenido
            age_pattern = r'\*CHI:\s*.*?(\d+)[;:]'
            match = re.search(age_pattern, content)
            if match:
                years = int(match.group(1))
                months = 0
                return f"{years} years {months:02d} months {days:02d} days"
            
            # Si no se encuentra la edad, devolver valor por defecto
            return "0 years 00 months 00 days"
            
        except Exception as e:
            print(f"Error al extraer la edad: {str(e)}")
            return "0 years 00 months 00 days"
    
    def extract_child_name(self, content, file_path=None):
        """Extrae el nombre del niño del contenido del archivo de Brend."""
        try:
            # Caso especial para Brend: extraer el nombre de la subcarpeta
            if file_path and 'Brent' in file_path:
                # El patrón será Brent/[a-z]\d+/ (por ejemplo, Brent/c1/, Brent/d1/, etc.)
                brend_pattern = r'Brent/([a-z]\d+)/'
                match = re.search(brend_pattern, file_path)
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
            if line.startswith('@ChildAge:') and age:
                new_lines.append(f'@ChildAge: {age}')
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
                    new_lines.append(f'@ChildAge: {age}')
                    age_added = True
                if child_name and not name_added:
                    new_lines.append(f'@ChildName: {child_name}')
                    name_added = True
        
        return '\n'.join(new_lines) 