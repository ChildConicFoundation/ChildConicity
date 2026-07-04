import os

from src.data_io.reader import Reader


def inspect_reader_output():
    # Create a Reader instance
    reader = Reader()
    
    # Read a test .cha file
    test_file = "Corpora_modified/VanKleeck/walter/walter1.cha"
    
    if not os.path.exists(test_file):
        print(f"Error: Test file not found: {test_file}")
        return
    
    # Read the file
    data = reader.read_cha(test_file)
    
    if data is None:
        print("Error reading file")
        return
    
    # Print metadata
    print("\nExtracted metadata:")
    print("-" * 50)
    for key, value in data['metadata'].items():
        print(f"{key}: {value}")
    print("-" * 50)

if __name__ == "__main__":
    inspect_reader_output()
