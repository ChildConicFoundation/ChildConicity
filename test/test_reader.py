import pytest
import os
import pandas as pd
from src.data_io.reader import Reader

@pytest.fixture
def reader():
    return Reader()

@pytest.fixture
def test_files():
    # Crear un archivo CSV de prueba
    test_csv_path = 'test_data.csv'
    pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']}).to_csv(test_csv_path, index=False)
    
    # Crear un archivo CHA de prueba
    test_cha_path = 'test_data.cha'
    with open(test_cha_path, 'w', encoding='utf-8') as f:
        f.write("""@UTF8
@PID: 11312/c-00017092-1
@Languages: spa
@Participants: CHI Target_Child, MOT Mother
@Options: CA
@Media: example, audio
@Date: 12-MAR-2024
@Types: long, free
*CHI: hola 1525_4985
*MOT: buenos días 1585_4985""")
    
    yield {'csv': test_csv_path, 'cha': test_cha_path}
    
    # Limpiar archivos después de las pruebas
    os.remove(test_csv_path)
    os.remove(test_cha_path)

def test_read_csv(reader, test_files):
    df = reader.read_csv(test_files['csv'])
    assert df is not None
    assert len(df) == 2
    assert list(df.columns) == ['col1', 'col2']

def test_read_cha(reader, test_files):
    data = reader.read_cha(test_files['cha'])
    assert data is not None
    
    metadata = data['metadata']
    assert metadata['encoding'] == 'UTF8'
    assert metadata['pid'] == '11312/c-00017092-1'
    assert metadata['languages'] == ['spa']
    assert len(metadata['participants']) == 2
    assert metadata['date'] == '12-MAR-2024'
    
    utterances = metadata['utterances']
    assert len(utterances) == 2
    assert utterances[0]['speaker'] == 'CHI'
    assert utterances[0]['timestamp']['start'] == 1525
    assert utterances[0]['timestamp']['end'] == 4985

def test_file_not_found(reader):
    assert reader.read_csv('nonexistent.csv') is None
    assert reader.read_cha('nonexistent.cha') is None


def test_extract_utterances_keeps_valid_single_letter_words(reader):
    content = """@UTF8
@Participants: CHI Target_Child, MOT Mother
*MOT: I want it .
"""

    utterances = reader._extract_utterances(content)

    assert len(utterances) == 1
    assert utterances[0]["text"] == "I want it"
