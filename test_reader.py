from src.data_io.reader import Reader
import os

def test_reader():
    # Crear instancia del Reader
    reader = Reader()
    
    # Leer un archivo .cha de prueba
    test_file = "Corpus_modified/VanKleeck/walter/walter1.cha"
    
    if not os.path.exists(test_file):
        print(f"Error: No se encontró el archivo de prueba {test_file}")
        return
    
    # Leer el archivo
    data = reader.read_cha(test_file)
    
    if data is None:
        print("Error al leer el archivo")
        return
    
    # Imprimir los metadatos
    print("\nMetadatos extraídos:")
    print("-" * 50)
    for key, value in data['metadata'].items():
        print(f"{key}: {value}")
    print("-" * 50)

if __name__ == "__main__":
    test_reader() 