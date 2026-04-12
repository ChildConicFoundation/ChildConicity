import pytest
from src.analysis.iconicity_model import IconicityModel

@pytest.fixture
def sample_data():
    return {
        1: {
            'word': 'casa',
            'n_ratings': 10,
            'n': 15,
            'prop_known': 0.8,
            'rating': 4.5,
            'rating_sd': 1.2
        },
        2: {
            'word': 'perro',
            'n_ratings': 12,
            'n': 15,
            'prop_known': 0.9,
            'rating': 3.8,
            'rating_sd': 1.0
        },
        3: {
            'word': 'gato',
            'n_ratings': 8,
            'n': 15,
            'prop_known': 0.7,
            'rating': 4.2,
            'rating_sd': 1.1
        }
    }

@pytest.fixture
def model(sample_data):
    return IconicityModel(sample_data)

def test_initialization(model):
    assert len(model.word_data) == 3
    assert 'casa' in model.word_data
    assert 'perro' in model.word_data
    assert 'gato' in model.word_data

def test_get_word_data(model):
    casa_data = model.get_word_data('casa')
    assert casa_data is not None
    assert casa_data['n_ratings'] == 10
    assert casa_data['rating'] == 4.5
    assert casa_data['prop_known'] == 0.8

def test_get_all_words(model):
    words = model.get_all_words()
    assert len(words) == 3
    assert 'casa' in words
    assert 'perro' in words
    assert 'gato' in words

def test_get_words_by_rating(model):
    # Palabras con rating >= 4.0
    high_rating_words = model.get_words_by_rating(min_rating=4.0)
    assert len(high_rating_words) == 2
    assert 'casa' in high_rating_words
    assert 'gato' in high_rating_words
    
    # Palabras con rating entre 3.5 y 4.0
    mid_rating_words = model.get_words_by_rating(min_rating=3.5, max_rating=4.0)
    assert len(mid_rating_words) == 1
    assert 'perro' in mid_rating_words

def test_get_words_by_known_proportion(model):
    # Palabras con prop_known >= 0.8
    high_prop_words = model.get_words_by_known_proportion(min_prop=0.8)
    assert len(high_prop_words) == 2
    assert 'casa' in high_prop_words
    assert 'perro' in high_prop_words
    
    # Palabras con prop_known <= 0.8
    low_prop_words = model.get_words_by_known_proportion(max_prop=0.8)
    assert len(low_prop_words) == 2
    assert 'casa' in low_prop_words
    assert 'gato' in low_prop_words

def test_invalid_word(model):
    assert model.get_word_data('nonexistent') is None

def test_iconicity_model():
    # Datos de prueba
    test_data = {
        1: {
            'word': 'hola',
            'n_ratings': 10,
            'n': 5,
            'prop_known': 0.8,
            'rating': 3.5,
            'rating_sd': 0.5
        },
        2: {
            'word': 'adiós',
            'n_ratings': 8,
            'n': 4,
            'prop_known': 0.9,
            'rating': 4.0,
            'rating_sd': 0.3
        }
    }
    
    # Crear instancia del modelo
    model = IconicityModel(test_data)
    
    # Verificar que los datos se procesaron correctamente
    hola_data = model.get_word_data('hola')
    assert hola_data is not None
    assert hola_data['n_ratings'] == 10
    assert hola_data['rating'] == 3.5
    assert hola_data['prop_known'] == 0.8
    
    adios_data = model.get_word_data('adiós')
    assert adios_data is not None
    assert adios_data['n_ratings'] == 8
    assert adios_data['rating'] == 4.0
    assert adios_data['prop_known'] == 0.9
    
    # Verificar que get_all_words devuelve todas las palabras
    assert set(model.get_all_words()) == {'hola', 'adiós'}
    
    # Verificar filtrado por rating
    high_rating_words = model.get_words_by_rating(min_rating=4.0)
    assert len(high_rating_words) == 1
    assert 'adiós' in high_rating_words
    
    # Verificar filtrado por proporción conocida
    high_known_words = model.get_words_by_known_proportion(min_prop=0.85)
    assert len(high_known_words) == 1
    assert 'adiós' in high_known_words

def test_get_all_word_data(model):
    """
    Prueba que get_all_word_data devuelve correctamente todo el diccionario de datos.
    """
    all_data = model.get_all_word_data()
    
    # Verificar que el diccionario contiene todas las palabras
    assert len(all_data) == 3
    
    # Verificar que los datos de cada palabra están completos
    assert 'casa' in all_data
    assert 'perro' in all_data
    assert 'gato' in all_data
    
    # Verificar que los datos de cada palabra son correctos
    casa_data = all_data['casa']
    assert casa_data['n_ratings'] == 10
    assert casa_data['n'] == 15
    assert casa_data['prop_known'] == 0.8
    assert casa_data['rating'] == 4.5
    assert casa_data['rating_sd'] == 1.2
    
    perro_data = all_data['perro']
    assert perro_data['n_ratings'] == 12
    assert perro_data['n'] == 15
    assert perro_data['prop_known'] == 0.9
    assert perro_data['rating'] == 3.8
    assert perro_data['rating_sd'] == 1.0
    
    gato_data = all_data['gato']
    assert gato_data['n_ratings'] == 8
    assert gato_data['n'] == 15
    assert gato_data['prop_known'] == 0.7
    assert gato_data['rating'] == 4.2
    assert gato_data['rating_sd'] == 1.1 


def test_iconicity_model_normalizes_word_lookup_case_insensitively():
    model = IconicityModel(
        {
            1: {
                "word": "Christmas",
                "n_ratings": 10,
                "n": 10,
                "prop_known": 1.0,
                "rating": 4.8,
                "rating_sd": 0.5,
            }
        }
    )

    assert "christmas" in model.get_all_words()
    assert model.get_word_data("christmas")["rating"] == 4.8
    assert model.get_word_data("CHRISTMAS")["rating"] == 4.8
