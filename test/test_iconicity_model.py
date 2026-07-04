import pytest
from src.analysis.iconicity_model import IconicityModel

@pytest.fixture
def sample_data():
    return {
        1: {
            'word': 'house',
            'n_ratings': 10,
            'n': 15,
            'prop_known': 0.8,
            'rating': 4.5,
            'rating_sd': 1.2
        },
        2: {
            'word': 'dog',
            'n_ratings': 12,
            'n': 15,
            'prop_known': 0.9,
            'rating': 3.8,
            'rating_sd': 1.0
        },
        3: {
            'word': 'cat',
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
    assert 'house' in model.word_data
    assert 'dog' in model.word_data
    assert 'cat' in model.word_data

def test_get_word_data(model):
    house_data = model.get_word_data('house')
    assert house_data is not None
    assert house_data['n_ratings'] == 10
    assert house_data['rating'] == 4.5
    assert house_data['prop_known'] == 0.8

def test_get_all_words(model):
    words = model.get_all_words()
    assert len(words) == 3
    assert 'house' in words
    assert 'dog' in words
    assert 'cat' in words

def test_get_words_by_rating(model):
    # Words with rating >= 4.0
    high_rating_words = model.get_words_by_rating(min_rating=4.0)
    assert len(high_rating_words) == 2
    assert 'house' in high_rating_words
    assert 'cat' in high_rating_words
    
    # Words with rating between 3.5 and 4.0
    mid_rating_words = model.get_words_by_rating(min_rating=3.5, max_rating=4.0)
    assert len(mid_rating_words) == 1
    assert 'dog' in mid_rating_words

def test_get_words_by_known_proportion(model):
    # Words with prop_known >= 0.8
    high_prop_words = model.get_words_by_known_proportion(min_prop=0.8)
    assert len(high_prop_words) == 2
    assert 'house' in high_prop_words
    assert 'dog' in high_prop_words
    
    # Words with prop_known <= 0.8
    low_prop_words = model.get_words_by_known_proportion(max_prop=0.8)
    assert len(low_prop_words) == 2
    assert 'house' in low_prop_words
    assert 'cat' in low_prop_words

def test_invalid_word(model):
    assert model.get_word_data('nonexistent') is None

def test_iconicity_model():
    # Test data
    test_data = {
        1: {
            'word': 'hello',
            'n_ratings': 10,
            'n': 5,
            'prop_known': 0.8,
            'rating': 3.5,
            'rating_sd': 0.5
        },
        2: {
            'word': 'goodbye',
            'n_ratings': 8,
            'n': 4,
            'prop_known': 0.9,
            'rating': 4.0,
            'rating_sd': 0.3
        }
    }
    
    # Create the model instance
    model = IconicityModel(test_data)
    
    # Check that the data was processed correctly
    hello_data = model.get_word_data('hello')
    assert hello_data is not None
    assert hello_data['n_ratings'] == 10
    assert hello_data['rating'] == 3.5
    assert hello_data['prop_known'] == 0.8
    
    goodbye_data = model.get_word_data('goodbye')
    assert goodbye_data is not None
    assert goodbye_data['n_ratings'] == 8
    assert goodbye_data['rating'] == 4.0
    assert goodbye_data['prop_known'] == 0.9
    
    # Check that get_all_words returns all words
    assert set(model.get_all_words()) == {'hello', 'goodbye'}
    
    # Check filtering by rating
    high_rating_words = model.get_words_by_rating(min_rating=4.0)
    assert len(high_rating_words) == 1
    assert 'goodbye' in high_rating_words
    
    # Check filtering by known proportion
    high_known_words = model.get_words_by_known_proportion(min_prop=0.85)
    assert len(high_known_words) == 1
    assert 'goodbye' in high_known_words

def test_get_all_word_data(model):
    """
    Test that get_all_word_data correctly returns the full data dictionary.
    """
    all_data = model.get_all_word_data()
    
    # Check that the dictionary contains all words
    assert len(all_data) == 3
    
    # Check that each word data is complete
    assert 'house' in all_data
    assert 'dog' in all_data
    assert 'cat' in all_data
    
    # Check that each word data is correct
    house_data = all_data['house']
    assert house_data['n_ratings'] == 10
    assert house_data['n'] == 15
    assert house_data['prop_known'] == 0.8
    assert house_data['rating'] == 4.5
    assert house_data['rating_sd'] == 1.2
    
    dog_data = all_data['dog']
    assert dog_data['n_ratings'] == 12
    assert dog_data['n'] == 15
    assert dog_data['prop_known'] == 0.9
    assert dog_data['rating'] == 3.8
    assert dog_data['rating_sd'] == 1.0
    
    cat_data = all_data['cat']
    assert cat_data['n_ratings'] == 8
    assert cat_data['n'] == 15
    assert cat_data['prop_known'] == 0.7
    assert cat_data['rating'] == 4.2
    assert cat_data['rating_sd'] == 1.1 


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
