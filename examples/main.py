import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corpus_normalizers.brent_normalizer import BrendManipulator

def main():
    """Main function for processing the Brend corpus"""
    # Configure paths
    base_dir = os.path.join("Corpora", "Brent")
    output_dir = os.path.join("Corpora", "Brent_modified")
    
    # Create the manipulator
    manipulator = BrendManipulator()
    manipulator.base_dir = base_dir
    manipulator.output_dir = output_dir
    
    # Read the directory
    reader = Reader()
    corpus_data = reader.read_directory(base_dir)
    
    # Process all .cha files
    formatter = DataFormatter()
    corpus_processed_data = process_cha_files(corpus_data)
    
    # Create a dictionary by directory
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
    
    # Show results
    print(f"\nResultados para {corpus_name}:")
    for directory, data in directory_data.items():
        print(f"\nDirectorio: {directory}")
        print(f"  Número de expresiones de niños: {len(data['children_data'])}")
        print(f"  Número de expresiones de adultos: {len(data['adults_data'])}")
        
        # Show examples
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
    """Recursively processes all .cha files in the directory structure"""
    result_dict = {}
    
    for dir_name, content in data.items():
        new_path = f"{current_path}/{dir_name}" if current_path else dir_name
        
        if 'files' in content:
            for file in content['files']:
                if file['metadata']['file_path'].endswith('.cha'):
                    file_path = file['metadata']['file_path']
                    print(f"Procesando archivo: {file_path}")
                    file_formatter = DataFormatter()
                    children_data, _, adults_data = file_formatter.format_cha_data_from(file_path)
                    
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
    # Process the CSV file first to get iconicity data
    print("Procesando archivo CSV:")
    formatter = DataFormatter()
    csv_data = formatter.format_csv_data_from('iconicity_ratings/iconicity_ratings_cleaned.csv')
    
    # Create the iconicity model
    iconicity_model = IconicityModel(csv_data)
    all_words = iconicity_model.get_all_word_data()
    
    # Process each corpus
    corpora = {
        'Brent': 'Corpora_modified/Brent',
        'VanKleeck': 'Corpora_modified/VanKleeck',
        'Post': 'Corpora_modified/Post',
        'NewEngland': 'Corpora_modified/NewEngland'
    }
    
    for corpus_name, corpus_path in corpora.items():
        process_corpus(corpus_name, corpus_path)

if __name__ == "__main__":
    main()

    # Process CSV file
    print("Procesando archivo CSV:")
    formatter = DataFormatter()
    csv_data = formatter.format_csv_data_from('iconicity_ratings/iconicity_ratings_cleaned.csv')
    if csv_data is not None:
        print("\nPrimeras 5 entradas del CSV:")
        for id, entry in list(csv_data.items())[:5]:
            print(f"\n{id}:")
            for key, value in entry.items():
                print(f"{key}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # Process .cha file
    print("Procesando archivo .cha:")
    children_data, _, adults_data = formatter.format_cha_data_from('record.cha')
    
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
    
    # Show .cha file metadata
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
    
    # Word analysis
    print("Análisis de palabras:")
    
    # Count words in child utterances
    print("\nPalabras más comunes en niños:")
    child_counter = WordCounter()
    child_counts = child_counter.count_words(children_data)
    print("\n10 palabras más comunes en niños:")
    for word, count in child_counter.get_most_common(10):
        print(f"{word}: {count} veces")
    
    print("\n" + "="*50 + "\n")
    
    # Count words in adult utterances
    print("Palabras más comunes en adultos:")
    adult_counter = WordCounter()
    adult_counts = adult_counter.count_words(adults_data)
    print("\n10 palabras más comunes en adultos:")
    for word, count in adult_counter.get_most_common(10):
        print(f"{word}: {count} veces")
    
    print("\n" + "="*50 + "\n")
    
    # Iconicity analysis
    print("Análisis de iconicidad:")
    
    # Check the contents of csv_data
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
    
    # Create the iconicity model
    iconicity_model = IconicityModel(csv_data)
    
    # Check the model contents
    print("\nVerificación del modelo de iconicidad:")
    all_words = iconicity_model.get_all_word_data()
    
    # Create a WordDictionaryMerger instance and add dictionaries
    merger = WordDictionaryMerger()
    merger.add_dictionary(all_words)
    merger.add_dictionary(adult_counts)
    # merger.add_dictionary(child_counts)
    
    # Get the merge
    merged_dict, unmerged_dictionaries = merger.obtain_merge()
    
    # Show some statistics
    print("\nEstadísticas del merge:")
    print(f"Número de palabras en el diccionario mergeado: {len(merged_dict)}")
    print(f"Número de diccionarios no mergeados: {len(unmerged_dictionaries)}")
    
    # Show some words from the merged dictionary
    print("\nEjemplos de palabras en el diccionario mergeado:")
    for i, (word, data) in enumerate(merged_dict.items()):
        if i < 5:  # Show only the first 5 words
            print(f"\nPalabra: {word}")
            print(f"Datos: {data}")

    # Sort the merged dictionary by rating from highest to lowest
    print("\nDiccionario mergeado ordenado por rating (de mayor a menor):")
    sorted_merged_dict = dict(sorted(
        merged_dict.items(),
        key=lambda x: x[1]['rating'],
        reverse=True
    ))
    
    # Show the first 10 sorted words
    print("\nTop 10 palabras por rating:")
    for i, (word, data) in enumerate(sorted_merged_dict.items()):
        if i >= 10:
            break
        print(f"{word}: Rating={data['rating']}, Count={data.get('count', 0)}")    

    # Read DirectorioBrent
    print("\n" + "="*50 + "\n")
    print("Leyendo Brent:")
    reader = Reader()
    corpus_data = reader.read_directory('Corpus')
    
    def print_directory_structure(data, level=0):
        """
        Prints the directory structure visually.
        
        Args:
            data (dict): Dictionary with the directory structure
            level (int): Current indentation level
        """
        for dir_name, content in data.items():
            # Print the directory name
            print("  " * level + "📁 " + dir_name)
            
            # If there are files, print them
            if 'files' in content:
                for file in content['files']:
                    print("  " * (level + 1) + "📄 " + file['metadata']['file_path'])
            
            # Process subdirectories
            for key, value in content.items():
                if key != 'files':
                    print_directory_structure({key: value}, level + 1)
    
    # Show the directory structure
    print("\nEstructura de Brent:")
    print_directory_structure(corpus_data)

    # Show the contents of a specific file
    print("\n" + "="*50 + "\n")
    print("Contenido del primer archivo encontrado:")
    
    # Get the contents of the first file found
    first_file = None
    for dir_name, content in corpus_data['Brent'].items():
        if 'files' in content and content['files']:
            first_file = content['files'][0]
            print(f"Archivo: {first_file['metadata']['file_path']}")
            break
    
    if first_file:
        # Show metadata
        print("\nMetadatos:")
        for key, value in first_file['metadata'].items():
            print(f"{key}: {value}")
        
        # Process the file using DataFormatter
        print("\nProcesando archivo con DataFormatter:")
        file_path = first_file['metadata']['file_path']
        children_data, _, adults_data = formatter.format_cha_data_from(file_path)
        
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

    # Process all .cha files en corpus_data
    print("\n" + "="*50 + "\n")
    print("Procesando archivos .cha en corpus_data:")
    
    def process_cha_files(data, current_path=""):
        """
        Recursively processes all .cha files in the directory structure.
        
        Args:
            data (dict): Dictionary with the directory structure
            current_path (str): Current path in the directory tree
        """
        result_dict = {}
            
        for dir_name, content in data.items():
            new_path = f"{current_path}/{dir_name}" if current_path else dir_name
            
            # Process files in the current directory
            if 'files' in content:
                for file in content['files']:
                    if file['metadata']['file_path'].endswith('.cha'):
                        file_path = file['metadata']['file_path']
                        print(f"Procesando archivo: {file_path}")
                        # Create a new formatter for each file
                        file_formatter = DataFormatter()
                        children_data, _, adults_data = file_formatter.format_cha_data_from(file_path)
                        
                        # Create a dictionary entry
                        if new_path not in result_dict:
                            result_dict[new_path] = {}
                            
                        filename = file_path.split('/')[-1]
                        result_dict[new_path][filename] = {
                            'children_data': children_data,
                            'adults_data': adults_data
                        }
            
            # Process subdirectories
            for key, value in content.items():
                if key != 'files':
                    subdir_results = process_cha_files({key: value}, new_path)
                    result_dict.update(subdir_results)
        
        return result_dict
    
    # Process all .cha files and get the resulting dictionary
    brent_processed_data = process_cha_files(corpus_data)
    
    # Create a dictionary by directory with merged data
    directory_data = {}
    
    # For each directory, merge the child and adult dictionaries
    for directory, files in brent_processed_data.items():
        # Extract only the directory name from the full path
        dir_name = directory.split('/')[-1]
        
        # Create separate WordDictionaryMerger instances for children and adults
        children_merger = WordDictionaryMerger()
        adults_merger = WordDictionaryMerger()
        
        # Add each file dictionary to the corresponding merger
        for filename, data in files.items():
            if data['children_data']:  # Check that child data exists
                children_merger.add_dictionary(data['children_data'])
            if data['adults_data']:  # Check that adult data exists
                adults_merger.add_dictionary(data['adults_data'])
        
        # Get the merged dictionaries
        merged_children, _ = children_merger.obtain_merge()
        merged_adults, _ = adults_merger.obtain_merge()
        
        # Store the merged data in the directory dictionary
        directory_data[dir_name] = {
            'children_data': merged_children,
            'adults_data': merged_adults
        }
    
    # Show the dictionary structure by directory
    print("\nEstructura del diccionario por directorio:")
    for directory, data in directory_data.items():
        print(f"\nDirectorio: {directory}")
        print(f"  Número de expresiones de niños: {len(data['children_data'])}")
        print(f"  Número de expresiones de adultos: {len(data['adults_data'])}")
        
        # Show some examples from each directory
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
    
    # Create a counter dictionary
    word_counter_dictionary = {}
    for directory, data in directory_data.items():
        # Create counters for children and adults
        directory_counter_children = WordCounter()
        directory_counter_children.count_words(data['children_data'])
        directory_counter_adults = WordCounter()
        directory_counter_adults.count_words(data['adults_data'])
        
        # Store both counters in the dictionary
        word_counter_dictionary[directory] = {
            'children': directory_counter_children,
            'adults': directory_counter_adults
        }

    # Print the first 5 dictionary entries
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
        # Get word counters for children and adults
        children_counts = counters['children'].get_word_counts()
        adults_counts = counters['adults'].get_word_counts()
        
        # Create dictionaries to store results
        children_merged = {}
        adults_merged = {}
        
        # Process child counts
        for word, count in children_counts.items():
            children_merged[word] = {'count': count}
            if word in all_words:
                children_merged[word].update(all_words[word])
        
        # Process adult counts
        for word, count in adults_counts.items():
            adults_merged[word] = {'count': count}
            if word in all_words:
                adults_merged[word].update(all_words[word])
        
        # Store results in the final dictionary
        final_merger[directory] = {
            'children': children_merged,
            'adults': adults_merged
        }
        
        # Print some results for verification
        print(f"\nResultados para el directorio {directory}:")
        print("\nPalabras más comunes en niños:")
        for word, data in sorted(children_merged.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            print(f"{word}: {data}")
        
        print("\nPalabras más comunes en adultos:")
        for word, data in sorted(adults_merged.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            print(f"{word}: {data}")
    
    for directory, data in final_merger.items():
        print(f"\nContiene el directorio {directory}:")
            
