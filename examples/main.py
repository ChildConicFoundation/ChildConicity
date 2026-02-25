import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corpus_normalizers.brent_normalizer import BrendManipulator

def main():
    """Función principal para procesar el corpus de Brend"""
    # Configurar rutas
    base_dir = os.path.join("Corpus", "Brent")
    output_dir = os.path.join("Corpus", "Brent_modified")
    
    # Crear el manipulador
    manipulator = BrendManipulator()
    manipulator.base_dir = base_dir
    manipulator.output_dir = output_dir
    
    # Leer el directorio
    reader = Reader()
    corpus_data = reader.read_directory(base_dir)
    
    # Procesar todos los archivos .cha
    formatter = DataFormatter()
    corpus_processed_data = process_cha_files(corpus_data)
    
    # Crear diccionario por directorio
    directory_data = {}
    for directory, files in corpus_processed_data.items():
        dir_name = directory.split('/')[-1]
        children_merger = WordDictionaryMerger()
        adults_merger = WordDictionaryMerger()
        
        for filename, data in files.items():
            if data['children_data']:
                children_merger.add_dictionary(data['children_data'])
            if data['adults_data']:
                adults_merger.add_dictionary(data['adults_data'])
        
        merged_children, _ = children_merger.obtain_merge()
        merged_adults, _ = adults_merger.obtain_merge()
        
        directory_data[dir_name] = {
            'children_data': merged_children,
            'adults_data': merged_adults
        }
    
    # Mostrar resultados
    print(f"\nResultados para {corpus_name}:")
    for directory, data in directory_data.items():
        print(f"\nDirectorio: {directory}")
        print(f"  Número de expresiones de niños: {len(data['children_data'])}")
        print(f"  Número de expresiones de adultos: {len(data['adults_data'])}")
        
        # Mostrar ejemplos
        print("\n  Ejemplos de expresiones de niños:")
        for i, (key, value) in enumerate(list(data['children_data'].items())[:3]):
            print(f"    {key}:")
            print(f"      Hablante: {value['speaker']}")
            print(f"      Texto: {value['text']}")
            if value['timestamp']:
                print(f"      Tiempo: {value['timestamp']['start']}-{value['timestamp']['end']}")
        
        print("\n  Ejemplos de expresiones de adultos:")
        for i, (key, value) in enumerate(list(data['adults_data'].items())[:3]):
            print(f"    {key}:")
            print(f"      Hablante: {value['speaker']}")
            print(f"      Texto: {value['text']}")
            if value['timestamp']:
                print(f"      Tiempo: {value['timestamp']['start']}-{value['timestamp']['end']}")

def process_cha_files(data, current_path=""):
    """Procesa recursivamente todos los archivos .cha en la estructura de directorios"""
    result_dict = {}
    
    for dir_name, content in data.items():
        new_path = f"{current_path}/{dir_name}" if current_path else dir_name
        
        if 'files' in content:
            for file in content['files']:
                if file['metadata']['file_path'].endswith('.cha'):
                    file_path = file['metadata']['file_path']
                    print(f"Procesando archivo: {file_path}")
                    file_formatter = DataFormatter()
                    children_data, adults_data = file_formatter.format_cha_data_from(file_path)
                    
                    if new_path not in result_dict:
                        result_dict[new_path] = {}
                    
                    filename = file_path.split('/')[-1]
                    result_dict[new_path][filename] = {
                        'children_data': children_data,
                        'adults_data': adults_data
                    }
        
        for key, value in content.items():
            if key != 'files':
                subdir_results = process_cha_files({key: value}, new_path)
                result_dict.update(subdir_results)
    
    return result_dict

def main():
    # Procesar el archivo CSV primero para tener los datos de iconicidad
    print("Procesando archivo CSV:")
    formatter = DataFormatter()
    csv_data = formatter.format_csv_data_from('iconicity_ratings_cleaned.csv')
    
    # Crear el modelo de iconicidad
    iconicity_model = IconicityModel(csv_data)
    all_words = iconicity_model.get_all_word_data()
    
    # Procesar cada corpus
    corpora = {
        'Brent': 'Corpus_modified/Brent',
        'VanKleeck': 'Corpus_modified/VanKleeck',
        'Post': 'Corpus_modified/Post',
        'NewEngland': 'Corpus_modified/NewEngland'
    }
    
    for corpus_name, corpus_path in corpora.items():
        process_corpus(corpus_name, corpus_path)

if __name__ == "__main__":
    main()

    # Procesar archivo CSV
    print("Procesando archivo CSV:")
    formatter = DataFormatter()
    csv_data = formatter.format_csv_data_from('iconicity_ratings_cleaned.csv')
    if csv_data is not None:
        print("\nPrimeras 5 entradas del CSV:")
        for id, entry in list(csv_data.items())[:5]:
            print(f"\n{id}:")
            for key, value in entry.items():
                print(f"{key}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # Procesar archivo .cha
    print("Procesando archivo .cha:")
    children_data, adults_data = formatter.format_cha_data_from('record.cha')
    
    print("\nPrimeras 10 expresiones de niños:")
    for id, entry in list(children_data.items())[:10]:
        print(f"\n{id}:")
        print(f"  Hablante: {entry['speaker']}")
        print(f"  Texto: {entry['text']}")
        if entry['timestamp']:
            print(f"  Tiempo: {entry['timestamp']['start']}-{entry['timestamp']['end']}")
    
    print("\n" + "="*50 + "\n")
    
    print("Primeras 10 expresiones de adultos:")
    for id, entry in list(adults_data.items())[:10]:
        print(f"\n{id}:")
        print(f"  Hablante: {entry['speaker']}")
        print(f"  Texto: {entry['text']}")
        if entry['timestamp']:
            print(f"  Tiempo: {entry['timestamp']['start']}-{entry['timestamp']['end']}")
    
    print("\n" + "="*50 + "\n")
    
    # Mostrar metadatos del archivo .cha
    print("Metadatos del archivo .cha:")
    reader = Reader()
    cha_data = reader.read_cha('record.cha')
    if cha_data is not None:
        metadata = cha_data['metadata']
        print(f"Codificación: {metadata['encoding']}")
        print(f"PID: {metadata['pid']}")
        print(f"Idiomas: {', '.join(metadata['languages'])}")
        print("\nParticipantes:")
        for code, name in metadata['participants'].items():
            print(f"  {code}: {name}")
        print(f"\nOpciones: {', '.join(metadata['options'])}")
        print(f"Medios: {metadata['media']['id']} ({metadata['media']['type']})")
        print(f"Fecha: {metadata['date']}")
        print(f"Tipos: {', '.join(metadata['types'])}")
    
    print("\n" + "="*50 + "\n")
    
    # Análisis de palabras
    print("Análisis de palabras:")
    
    # Contar palabras en las expresiones de niños
    print("\nPalabras más comunes en niños:")
    child_counter = WordCounter()
    child_counts = child_counter.count_words(children_data)
    print("\n10 palabras más comunes en niños:")
    for word, count in child_counter.get_most_common(10):
        print(f"{word}: {count} veces")
    
    print("\n" + "="*50 + "\n")
    
    # Contar palabras en las expresiones de adultos
    print("Palabras más comunes en adultos:")
    adult_counter = WordCounter()
    adult_counts = adult_counter.count_words(adults_data)
    print("\n10 palabras más comunes en adultos:")
    for word, count in adult_counter.get_most_common(10):
        print(f"{word}: {count} veces")
    
    print("\n" + "="*50 + "\n")
    
    # Análisis de iconicidad
    print("Análisis de iconicidad:")
    
    # Verificar el contenido de csv_data
    print("\nVerificación de datos CSV:")
    if csv_data is None:
        print("Error: No se pudieron cargar los datos del CSV")
    else:
        print(f"Total de entradas en CSV: {len(csv_data)}")
        if len(csv_data) > 0:
            first_entry = next(iter(csv_data.values()))
            print("\nEstructura de una entrada:")
            for key, value in first_entry.items():
                print(f"{key}: {value}")
    
    # Crear el modelo de iconicidad
    iconicity_model = IconicityModel(csv_data)
    
    # Verificar el contenido del modelo
    print("\nVerificación del modelo de iconicidad:")
    all_words = iconicity_model.get_all_word_data()
    
    # Crear instancia de WordDictionaryMerger y añadir diccionarios
    merger = WordDictionaryMerger()
    merger.add_dictionary(all_words)
    merger.add_dictionary(adult_counts)
    # merger.add_dictionary(child_counts)
    
    # Obtener el merge
    merged_dict, unmerged_dictionaries = merger.obtain_merge()
    
    # Mostrar algunas estadísticas
    print("\nEstadísticas del merge:")
    print(f"Número de palabras en el diccionario mergeado: {len(merged_dict)}")
    print(f"Número de diccionarios no mergeados: {len(unmerged_dictionaries)}")
    
    # Mostrar algunas palabras del diccionario mergeado
    print("\nEjemplos de palabras en el diccionario mergeado:")
    for i, (word, data) in enumerate(merged_dict.items()):
        if i < 5:  # Mostrar solo las primeras 5 palabras
            print(f"\nPalabra: {word}")
            print(f"Datos: {data}")

    # Ordenar el diccionario mergeado por rating de mayor a menor
    print("\nDiccionario mergeado ordenado por rating (de mayor a menor):")
    sorted_merged_dict = dict(sorted(
        merged_dict.items(),
        key=lambda x: x[1]['rating'],
        reverse=True
    ))
    
    # Mostrar las primeras 10 palabras ordenadas
    print("\nTop 10 palabras por rating:")
    for i, (word, data) in enumerate(sorted_merged_dict.items()):
        if i >= 10:
            break
        print(f"{word}: Rating={data['rating']}, Count={data.get('count', 0)}")    

    # Leer el DirectorioBrent
    print("\n" + "="*50 + "\n")
    print("Leyendo Brent:")
    reader = Reader()
    corpus_data = reader.read_directory('Corpus')
    
    def print_directory_structure(data, level=0):
        """
        Imprime la estructura del directorio de forma visual.
        
        Args:
            data (dict): Diccionario con la estructura del directorio
            level (int): Nivel de indentación actual
        """
        for dir_name, content in data.items():
            # Imprimir el nombre del directorio
            print("  " * level + "📁 " + dir_name)
            
            # Si hay archivos, imprimirlos
            if 'files' in content:
                for file in content['files']:
                    print("  " * (level + 1) + "📄 " + file['metadata']['file_path'])
            
            # Procesar subdirectorios
            for key, value in content.items():
                if key != 'files':
                    print_directory_structure({key: value}, level + 1)
    
    # Mostrar la estructura del directorio
    print("\nEstructura de Brent:")
    print_directory_structure(corpus_data)

    # Mostrar el contenido de un archivo específico
    print("\n" + "="*50 + "\n")
    print("Contenido del primer archivo encontrado:")
    
    # Obtener el contenido del primer archivo que encontremos
    first_file = None
    for dir_name, content in corpus_data['Brent'].items():
        if 'files' in content and content['files']:
            first_file = content['files'][0]
            print(f"Archivo: {first_file['metadata']['file_path']}")
            break
    
    if first_file:
        # Mostrar metadatos
        print("\nMetadatos:")
        for key, value in first_file['metadata'].items():
            print(f"{key}: {value}")
        
        # Procesar el archivo usando DataFormatter
        print("\nProcesando archivo con DataFormatter:")
        file_path = first_file['metadata']['file_path']
        children_data, adults_data = formatter.format_cha_data_from(file_path)
        
        print("\nPrimeras 10 expresiones de niños:")
        for id, entry in list(children_data.items())[:10]:
            print(f"\n{id}:")
            print(f"  Hablante: {entry['speaker']}")
            print(f"  Texto: {entry['text']}")
            if entry['timestamp']:
                print(f"  Tiempo: {entry['timestamp']['start']}-{entry['timestamp']['end']}")
        
        print("\nPrimeras 10 expresiones de adultos:")
        for id, entry in list(adults_data.items())[:10]:
            print(f"\n{id}:")
            print(f"  Hablante: {entry['speaker']}")
            print(f"  Texto: {entry['text']}")
            if entry['timestamp']:
                print(f"  Tiempo: {entry['timestamp']['start']}-{entry['timestamp']['end']}")

    # Procesar todos los archivos .cha en corpus_data
    print("\n" + "="*50 + "\n")
    print("Procesando archivos .cha en corpus_data:")
    
    def process_cha_files(data, current_path=""):
        """
        Procesa recursivamente todos los archivos .cha en la estructura de directorios.
        
        Args:
            data (dict): Diccionario con la estructura del directorio
            current_path (str): Ruta actual en el árbol de directorios
        """
        result_dict = {}
            
        for dir_name, content in data.items():
            new_path = f"{current_path}/{dir_name}" if current_path else dir_name
            
            # Procesar archivos en el directorio actual
            if 'files' in content:
                for file in content['files']:
                    if file['metadata']['file_path'].endswith('.cha'):
                        file_path = file['metadata']['file_path']
                        print(f"Procesando archivo: {file_path}")
                        # Crear un nuevo formatter para cada archivo
                        file_formatter = DataFormatter()
                        children_data, adults_data = file_formatter.format_cha_data_from(file_path)
                        
                        # Crear entrada en el diccionario
                        if new_path not in result_dict:
                            result_dict[new_path] = {}
                            
                        filename = file_path.split('/')[-1]
                        result_dict[new_path][filename] = {
                            'children_data': children_data,
                            'adults_data': adults_data
                        }
            
            # Procesar subdirectorios
            for key, value in content.items():
                if key != 'files':
                    subdir_results = process_cha_files({key: value}, new_path)
                    result_dict.update(subdir_results)
        
        return result_dict
    
    # Procesar todos los archivos .cha y obtener el diccionario resultante
    brent_processed_data = process_cha_files(corpus_data)
    
    # Crear un diccionario por directorio con los datos fusionados
    directory_data = {}
    
    # Para cada directorio, fusionar los diccionarios de niños y adultos
    for directory, files in brent_processed_data.items():
        # Extraer solo el nombre del directorio de la ruta completa
        dir_name = directory.split('/')[-1]
        
        # Crear instancias separadas de WordDictionaryMerger para niños y adultos
        children_merger = WordDictionaryMerger()
        adults_merger = WordDictionaryMerger()
        
        # Añadir los diccionarios de cada archivo al merger correspondiente
        for filename, data in files.items():
            if data['children_data']:  # Verificar que hay datos de niños
                children_merger.add_dictionary(data['children_data'])
            if data['adults_data']:  # Verificar que hay datos de adultos
                adults_merger.add_dictionary(data['adults_data'])
        
        # Obtener los diccionarios fusionados
        merged_children, _ = children_merger.obtain_merge()
        merged_adults, _ = adults_merger.obtain_merge()
        
        # Almacenar los datos fusionados en el diccionario del directorio
        directory_data[dir_name] = {
            'children_data': merged_children,
            'adults_data': merged_adults
        }
    
    # Mostrar la estructura del diccionario por directorio
    print("\nEstructura del diccionario por directorio:")
    for directory, data in directory_data.items():
        print(f"\nDirectorio: {directory}")
        print(f"  Número de expresiones de niños: {len(data['children_data'])}")
        print(f"  Número de expresiones de adultos: {len(data['adults_data'])}")
        
        # Mostrar algunos ejemplos de cada directorio
        print("\n  Ejemplos de expresiones de niños:")
        for i, (key, value) in enumerate(list(data['children_data'].items())[:3]):
            print(f"    {key}:")
            print(f"      Hablante: {value['speaker']}")
            print(f"      Texto: {value['text']}")
            if value['timestamp']:
                print(f"      Tiempo: {value['timestamp']['start']}-{value['timestamp']['end']}")
        
        print("\n  Ejemplos de expresiones de adultos:")
        for i, (key, value) in enumerate(list(data['adults_data'].items())[:3]):
            print(f"    {key}:")
            print(f"      Hablante: {value['speaker']}")
            print(f"      Texto: {value['text']}")
            if value['timestamp']:
                print(f"      Tiempo: {value['timestamp']['start']}-{value['timestamp']['end']}")
    
    # Crear diccionario de contadores
    word_counter_dictionary = {}
    for directory, data in directory_data.items():
        # Crear contadores para niños y adultos
        directory_counter_children = WordCounter()
        directory_counter_children.count_words(data['children_data'])
        directory_counter_adults = WordCounter()
        directory_counter_adults.count_words(data['adults_data'])
        
        # Almacenar ambos contadores en el diccionario
        word_counter_dictionary[directory] = {
            'children': directory_counter_children,
            'adults': directory_counter_adults
        }

    # Imprimir las primeras 5 entradas del diccionario
    print("\nPrimeras 5 entradas del diccionario word_counter_dictionary:")
    for i, (directory, counters) in enumerate(list(word_counter_dictionary.items())[:5]):
        print(f"\n{i+1}. Directorio: {directory}")
        print("\nContador de niños:")
        print(counters['children'].get_word_counts())
        print("\nContador de adultos:")
        print(counters['adults'].get_word_counts())
        print("\n" + "="*50)

    final_merger = {}
    for directory, counters in word_counter_dictionary.items():
        # Obtener los contadores de palabras para niños y adultos
        children_counts = counters['children'].get_word_counts()
        adults_counts = counters['adults'].get_word_counts()
        
        # Crear diccionarios para almacenar los resultados
        children_merged = {}
        adults_merged = {}
        
        # Procesar conteos de niños
        for word, count in children_counts.items():
            children_merged[word] = {'count': count}
            if word in all_words:
                children_merged[word].update(all_words[word])
        
        # Procesar conteos de adultos
        for word, count in adults_counts.items():
            adults_merged[word] = {'count': count}
            if word in all_words:
                adults_merged[word].update(all_words[word])
        
        # Almacenar los resultados en el diccionario final
        final_merger[directory] = {
            'children': children_merged,
            'adults': adults_merged
        }
        
        # Imprimir algunos resultados para verificación
        print(f"\nResultados para el directorio {directory}:")
        print("\nPalabras más comunes en niños:")
        for word, data in sorted(children_merged.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            print(f"{word}: {data}")
        
        print("\nPalabras más comunes en adultos:")
        for word, data in sorted(adults_merged.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            print(f"{word}: {data}")
    
    for directory, data in final_merger.items():
        print(f"\nContiene el directorio {directory}:")
            
