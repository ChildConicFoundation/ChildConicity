import re
from collections import defaultdict

class WordCounter:
    """
    Class for counting words in text.
    """
    
    def __init__(self):
        """
        Initializes the word counter.
        """
        self.word_counts = defaultdict(int)
    
    def count_words(self, data):
        """
        Counts words in the provided text.
        
        Args:
            data (str or dict): String with text or dictionary with 'text' fields to process.
        """
        # If data is a string, process it directly
        if isinstance(data, str):
            words = re.findall(r'\b\w+\b', data.lower())
            for word in words:
                self.word_counts[word] += 1
        # If data is a dictionary, process each entry
        elif isinstance(data, dict):
            if 'text' in data:
                words = re.findall(r'\b\w+\b', data['text'].lower())
                for word in words:
                    self.word_counts[word] += 1
            else:
                for entry in data.values():
                    if isinstance(entry, dict) and 'text' in entry:
                        words = re.findall(r'\b\w+\b', entry['text'].lower())
                        for word in words:
                            self.word_counts[word] += 1
    
    def get_word_counts(self):
        """
        Gets the word count dictionary.
        
        Returns:
            dict: Dictionary with words as keys and count dictionaries as values.
        """
        result = {}
        for word, count in self.word_counts.items():
            result[word] = {'count': count}
        return result
    
    def get_most_common(self, n=10):
        """
        Gets the n most common words.
        
        Args:
            n (int): Number of words to return.
            
        Returns:
            list: List of tuples (word, count) sorted by frequency.
        """
        # Sort by count and then alphabetically to break ties
        return sorted(self.word_counts.items(), 
                     key=lambda x: (-x[1], x[0]))[:n]
    
    def clear(self):
        """
        Clears the word counter.
        """
        self.word_counts.clear() 