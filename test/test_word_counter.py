import pytest
from src.analysis.word_counter import WordCounter

@pytest.fixture
def word_counter():
    return WordCounter()

def test_count_words(word_counter):
    # Test data
    test_data = {
        1: {'text': 'hola mundo hola'},
        2: {'text': 'mundo python'},
        3: {'text': 'hola python'}
    }
    
    # Count words
    word_counter.count_words(test_data)
    counts = word_counter.get_word_counts()
    
    # Check results
    assert counts['hola']['count'] == 3
    assert counts['mundo']['count'] == 2
    assert counts['python']['count'] == 2

def test_empty_data(word_counter):
    # Test with an empty dictionary
    word_counter.count_words({})
    counts = word_counter.get_word_counts()
    assert len(counts) == 0

def test_no_text_field(word_counter):
    # Test with entries that do not have a 'text' field
    test_data = {
        1: {'other': 'data'},
        2: {'more': 'data'}
    }
    word_counter.count_words(test_data)
    counts = word_counter.get_word_counts()
    assert len(counts) == 0

def test_get_most_common(word_counter):
    # Test data
    test_data = {
        1: {'text': 'hola mundo hola'},
        2: {'text': 'mundo python'},
        3: {'text': 'hola python'}
    }
    
    # Count words
    word_counter.count_words(test_data)
    
    # Get the most common words
    most_common = word_counter.get_most_common(2)
    assert most_common[0] == ('hola', 3)  # 'hola' appears 3 times
    assert most_common[1] == ('mundo', 2)  # 'mundo' appears 2 times

def test_case_insensitive(word_counter):
    # Data with different capitalization
    test_data = {
        1: {'text': 'Hola MUNDO hola'},
        2: {'text': 'mundo Python'}
    }
    
    # Count words
    word_counter.count_words(test_data)
    counts = word_counter.get_word_counts()
    
    # Check results
    assert counts['hola']['count'] == 2
    assert counts['mundo']['count'] == 2
    assert counts['python']['count'] == 1 