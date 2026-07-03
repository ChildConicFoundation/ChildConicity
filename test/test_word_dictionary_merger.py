import pytest
from src.analysis.word_dictionary_merger import WordDictionaryMerger

@pytest.fixture
def merger():
    return WordDictionaryMerger()

@pytest.fixture
def sample_dictionaries():
    return [
        {
            'casa': {'n_ratings': 10, 'rating': 4.5},
            'perro': {'n_ratings': 12, 'rating': 3.8},
            'gato': {'n_ratings': 8, 'rating': 4.2}
        },
        {
            'casa': {'prop_known': 0.8, 'rating_sd': 1.2},
            'perro': {'prop_known': 0.9, 'rating_sd': 1.0},
            'mesa': {'prop_known': 0.7, 'rating_sd': 1.1}
        },
        {
            'casa': {'frequency': 100, 'length': 4},
            'perro': {'frequency': 80, 'length': 5},
            'silla': {'frequency': 60, 'length': 5}
        }
    ]

def test_initialization(merger):
    assert len(merger.dictionaries) == 0

def test_add_dictionary(merger, sample_dictionaries):
    merger.add_dictionary(sample_dictionaries[0])
    assert len(merger.dictionaries) == 1
    assert merger.dictionaries[0] == sample_dictionaries[0]

def test_add_invalid_dictionary(merger):
    with pytest.raises(ValueError):
        merger.add_dictionary("not_a_dictionary")

def test_obtain_merge_empty(merger):
    merged, unmerged = merger.obtain_merge()
    assert merged == {}
    assert unmerged == []

def test_obtain_merge(merger, sample_dictionaries):
    for dictionary in sample_dictionaries:
        merger.add_dictionary(dictionary)
    
    merged, unmerged = merger.obtain_merge()
    
    # Check common words (casa and perro)
    assert 'casa' in merged
    assert 'perro' in merged
    assert 'gato' not in merged
    assert 'mesa' not in merged
    assert 'silla' not in merged
    
    # Check merged data
    assert merged['casa'] == {
        'n_ratings': 10,
        'rating': 4.5,
        'prop_known': 0.8,
        'rating_sd': 1.2,
        'frequency': 100,
        'length': 4
    }
    
    # Check unmerged dictionaries
    assert len(unmerged) == 3
    assert 'gato' in unmerged[0]
    assert 'mesa' in unmerged[1]
    assert 'silla' in unmerged[2]

def test_sort_by_parameter_gt():
    """Test sorting words with ratings greater than a threshold"""
    merger = WordDictionaryMerger()
    
    # Add test dictionaries
    dict1 = {
        'casa': {'rating': 4.5, 'prop_knwn': 0.9},
        'perro': {'rating': 3.8, 'prop_knwn': 0.8},
        'gato': {'rating': 4.2, 'prop_knwn': 0.7}
    }
    
    dict2 = {
        'casa': {'n_ratings': 10},
        'perro': {'n_ratings': 8},
        'gato': {'n_ratings': 12}
    }
    
    merger.add_dictionary(dict1)
    merger.add_dictionary(dict2)
    
    # Sort by rating > 4.0
    sorted_words = merger.sort_by_parameter('rating', 'gt', 4.0)
    
    # Check that it only contains words with rating > 4.0
    assert len(sorted_words) == 2
    assert 'casa' in sorted_words
    assert 'gato' in sorted_words
    assert 'perro' not in sorted_words
    
    # Check that it is sorted from highest to lowest rating
    words = list(sorted_words.keys())
    assert words[0] == 'casa'  # rating 4.5
    assert words[1] == 'gato'  # rating 4.2

def test_sort_by_parameter_lt():
    """Test sorting words with prop_knwn below a threshold"""
    merger = WordDictionaryMerger()
    
    # Add test dictionaries
    dict1 = {
        'casa': {'rating': 4.5, 'prop_knwn': 0.9},
        'perro': {'rating': 3.8, 'prop_knwn': 0.8},
        'gato': {'rating': 4.2, 'prop_knwn': 0.7}
    }
    
    merger.add_dictionary(dict1)
    
    # Sort by prop_knwn < 0.8
    sorted_words = merger.sort_by_parameter('prop_knwn', 'lt', 0.8)
    
    # Check that it only contains words with prop_knwn < 0.8
    assert len(sorted_words) == 1
    assert 'gato' in sorted_words
    assert 'casa' not in sorted_words
    assert 'perro' not in sorted_words

def test_sort_by_parameter_no_threshold():
    """Test sorting words without a threshold"""
    merger = WordDictionaryMerger()
    
    # Add test dictionaries
    dict1 = {
        'casa': {'rating': 4.5},
        'perro': {'rating': 3.8},
        'gato': {'rating': 4.2}
    }
    
    merger.add_dictionary(dict1)
    
    # Sort by rating without a threshold
    sorted_words = merger.sort_by_parameter('rating', 'gt')
    
    # Check that it contains all words
    assert len(sorted_words) == 3
    
    # Check that it is sorted from highest to lowest rating
    words = list(sorted_words.keys())
    assert words[0] == 'casa'  # rating 4.5
    assert words[1] == 'gato'  # rating 4.2
    assert words[2] == 'perro'  # rating 3.8

def test_sort_by_parameter_invalid_parameter():
    """Test invalid parameter"""
    merger = WordDictionaryMerger()
    
    dict1 = {'casa': {'rating': 4.5}}
    merger.add_dictionary(dict1)
    
    # Try sorting by a parameter that does not exist
    sorted_words = merger.sort_by_parameter('invalid_param', 'gt')
    assert len(sorted_words) == 0

def test_sort_by_parameter_non_numeric():
    """Test non-numeric values"""
    merger = WordDictionaryMerger()
    
    dict1 = {
        'casa': {'rating': 'high'},
        'perro': {'rating': 3.8}
    }
    
    merger.add_dictionary(dict1)
    
    # Sort by rating, ignoring the non-numeric value
    sorted_words = merger.sort_by_parameter('rating', 'gt')
    assert len(sorted_words) == 1
    assert 'perro' in sorted_words
    assert 'casa' not in sorted_words 