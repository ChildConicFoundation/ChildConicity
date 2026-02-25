import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corpus_normalizers.brent_normalizer import BrendManipulator
from src.corpus_normalizers.newengland_normalizer import process_directory as process_newengland
from src.corpus_normalizers.post_normalizer import process_directory as process_post
from src.corpus_normalizers.vankleeck_normalizer import process_directory as process_vankleeck

def initialize_brent_corpus():
    """Inicializa el corpus de Brent"""
    print("\nInicializando corpus de Brent...")
    
    # Configurar rutas
    base_dir = os.path.join("Corpus", "Brent")
    output_dir = os.path.join("Corpus_modified", "Brent")
    
    # Crear el manipulador
    manipulator = BrendManipulator()
    manipulator.base_dir = base_dir
    manipulator.output_dir = output_dir
    
    # Procesar el directorio
    manipulator.process_directory()
    print("¡Corpus de Brent inicializado!")

def initialize_new_england_corpus():
    """Inicializa el corpus de NewEngland"""
    print("\nInicializando corpus de NewEngland...")
    
    # Configurar rutas
    input_dir = os.path.join("Corpus", "NewEngland")
    output_dir = os.path.join("Corpus_modified", "NewEngland")
    
    # Procesar el directorio usando la función process_directory
    process_newengland(input_dir, output_dir)
    print("¡Corpus de NewEngland inicializado!")

def initialize_post_corpus():
    """Inicializa el corpus de Post"""
    print("\nInicializando corpus de Post...")
    
    # Configurar rutas
    input_dir = os.path.join("Corpus", "Post")
    output_dir = os.path.join("Corpus_modified", "Post")
    
    # Procesar el directorio usando la función process_directory de modify_post_files
    process_post(input_dir, output_dir)
    print("¡Corpus de Post inicializado!")

def initialize_van_kleeck_corpus():
    """Inicializa el corpus de VanKleeck"""
    print("\nInicializando corpus de VanKleeck...")
    
    # Configurar rutas
    input_dir = os.path.join("Corpus", "VanKleeck")
    output_dir = os.path.join("Corpus_modified", "VanKleeck")
    
    # Procesar el directorio usando la función process_directory de modify_vankleeck_files
    process_vankleeck(input_dir, output_dir)
    print("¡Corpus de VanKleeck inicializado!")

def main():
    """Función principal para inicializar todos los corpus"""
    print("Iniciando inicialización de corpus...")
    
    # Inicializar cada corpus
    initialize_brent_corpus()
    initialize_new_england_corpus()
    initialize_post_corpus()
    initialize_van_kleeck_corpus()
    
    print("\n¡Inicialización de corpus completada!")

if __name__ == "__main__":
    main() 