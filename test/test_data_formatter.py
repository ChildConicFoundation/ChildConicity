import pytest
import os
import pandas as pd
from src.data_io.data_formatter import DataFormatter

@pytest.fixture
def formatter():
    return DataFormatter()

@pytest.fixture
def test_files():
    # Crear archivo CSV de prueba
    test_csv_path = 'test_data.csv'
    pd.DataFrame({
        'word': ['casa', 'perro'],
        'rating': [4.5, 3.8]
    }).to_csv(test_csv_path, index=False)
    
    # Crear archivo CHA de prueba
    test_cha_path = 'test_data.cha'
    with open(test_cha_path, 'w', encoding='utf-8') as f:
        f.write("""@UTF8
@Participants: CHI Target_Child, MOT Mother
*CHI: hola 1525_4985
*MOT: buenos días 1555_4975
*CHI: adiós 1585_7985""")
    
    yield {'csv': test_csv_path, 'cha': test_cha_path}
    
    # Limpiar archivos después de las pruebas
    os.remove(test_csv_path)
    os.remove(test_cha_path)

def test_is_children(formatter):
    assert formatter.is_children('CHI') is True
    assert formatter.is_children('JEN', {'CHI', 'JEN'}) is True
    assert formatter.is_children('MOT') is False
    assert formatter.classify_speaker('CHI') == "target_child"
    assert formatter.classify_speaker('JEN', {'CHI'}, {'JEN'}) == "other_child"
    assert formatter.classify_speaker('MOT', {'CHI'}, {'JEN'}) == "adult"

def test_format_csv_data(formatter, test_files):
    data = formatter.format_csv_data_from(test_files['csv'])
    assert data is not None
    assert len(data) == 2
    assert data[1]['word'] == 'casa'

def test_format_cha_data(formatter, test_files):
    children_data, other_children_data, adults_data = formatter.format_cha_data_from(
        test_files['cha']
    )
    
    assert children_data is not None
    assert other_children_data is not None
    assert adults_data is not None
    
    # Verificar datos de niños
    assert len(children_data) == 2
    assert children_data[1]['text'].strip() == 'hola'
    
    # Verificar datos de adultos
    assert len(adults_data) == 1
    assert adults_data[1]['text'].strip() == 'buenos días'
    assert len(other_children_data) == 0

def test_get_data_methods(formatter, test_files):
    formatter.format_cha_data_from(test_files['cha'])
    
    children_data = formatter.get_children_data()
    other_children_data = formatter.get_other_children_data()
    adults_data = formatter.get_adults_data()
    
    assert children_data is not None
    assert other_children_data is not None
    assert adults_data is not None
    assert len(children_data) == 2
    assert len(other_children_data) == 0
    assert len(adults_data) == 1


def test_format_cha_data_separates_non_target_children(tmp_path):
    test_cha_path = tmp_path / "child_roles.cha"
    test_cha_path.write_text(
        """@UTF8
@Languages: eng
@Participants: CHI Target_Child, JEN Sister, MOT Mother
@ID: eng|Bloom|CHI|2;00.10|male|TD||Target_Child|||
@ID: eng|Bloom|JEN|||||Sister|||
@ID: eng|Bloom|MOT||female|||Mother|||
*CHI: hola .
*JEN: yo también .
*MOT: buenos días .
""",
        encoding="utf-8",
    )

    formatter = DataFormatter()
    children_data, other_children_data, adults_data = formatter.format_cha_data_from(
        str(test_cha_path)
    )

    assert len(children_data) == 1
    assert children_data[1]["speaker"] == "CHI"
    assert len(other_children_data) == 1
    assert other_children_data[1]["speaker"] == "JEN"
    assert len(adults_data) == 1
    assert adults_data[1]["speaker"] == "MOT"


def test_format_cha_data_separates_playmates_as_other_children(tmp_path):
    test_cha_path = tmp_path / "playmate_roles.cha"
    test_cha_path.write_text(
        """@UTF8
@Languages: eng
@Participants: CHI Target_Child, JEN Playmate, MOT Mother
@ID: eng|Sachs|CHI|2;05.05|female|||Target_Child|||
@ID: eng|Sachs|JEN|||||Playmate|||
@ID: eng|Sachs|MOT||female|||Mother|||
*CHI: mío .
*JEN: no .
*MOT: comparte .
""",
        encoding="utf-8",
    )

    formatter = DataFormatter()
    children_data, other_children_data, adults_data = formatter.format_cha_data_from(
        str(test_cha_path)
    )

    assert len(children_data) == 1
    assert children_data[1]["speaker"] == "CHI"
    assert len(other_children_data) == 1
    assert other_children_data[1]["speaker"] == "JEN"
    assert len(adults_data) == 1
    assert adults_data[1]["speaker"] == "MOT"
