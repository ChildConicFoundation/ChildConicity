class WordDictionaryMerger:
    def __init__(self):
        """
        Initializes the merger with an empty array of dictionaries.
        """
        self.dictionaries = []
    
    def add_dictionary(self, dictionary):
        """
        Adds a new dictionary to the array.
        
        Args:
            dictionary (dict): Dictionary with strings as primary keys
        """
        if not isinstance(dictionary, dict):
            raise ValueError("The parameter must be a dictionary")
        self.dictionaries.append(dictionary)
    
    def sort_by_parameter(self, parameter, comparison_op, threshold=None):
        """
        Sorts words based on a parameter and a comparison operation.
        
        Args:
            parameter (str): Name of the parameter to sort by
            comparison_op (str): Comparison operation ('gt' for greater than, 'lt' for less than)
            threshold (float, optional): Threshold value for the comparison
            
        Returns:
            dict: Dictionary with words that meet the condition, sorted by the parameter
        """
        if not self.dictionaries:
            return {}
            
        # Get all words and their data
        all_words_data = {}
        for dictionary in self.dictionaries:
            for word, data in dictionary.items():
                if word not in all_words_data:
                    all_words_data[word] = data
                else:
                    all_words_data[word].update(data)
        
        # Filter and sort according to the condition
        filtered_words = {}
        for word, data in all_words_data.items():
            if parameter in data:
                value = data[parameter]
                if isinstance(value, (int, float)):
                    if comparison_op == 'gt' and (threshold is None or value > threshold):
                        filtered_words[word] = data
                    elif comparison_op == 'lt' and (threshold is None or value < threshold):
                        filtered_words[word] = data
        
        # Sort the dictionary by the parameter
        sorted_words = dict(sorted(
            filtered_words.items(),
            key=lambda x: x[1][parameter],
            reverse=(comparison_op == 'gt')
        ))
        
        return sorted_words
    
    def obtain_merge(self):
        """
        Gets two results:
        1. A dictionary with words that appear in all dictionaries, merging their data
        2. An array with dictionaries of words that could not be merged
        
        Returns:
            tuple: (merged_dict, unmerged_dictionaries)
        """
        if not self.dictionaries:
            return {}, []
        
        # Get all unique words
        all_words = set()
        for dictionary in self.dictionaries:
            all_words.update(dictionary.keys())
        
        # Find words common to all dictionaries
        common_words = set(all_words)
        for dictionary in self.dictionaries:
            common_words.intersection_update(dictionary.keys())
        
        # Create the merged dictionary
        merged_dict = {}
        for word in common_words:
            merged_data = {}
            for dictionary in self.dictionaries:
                merged_data.update(dictionary[word])
            merged_dict[word] = merged_data
        
        # Create the unmerged dictionaries
        unmerged_dictionaries = []
        for dictionary in self.dictionaries:
            unmerged_dict = {}
            for word, data in dictionary.items():
                if word not in common_words:
                    unmerged_dict[word] = data
            if unmerged_dict:  # Only add if there are unmerged words
                unmerged_dictionaries.append(unmerged_dict)
        
        return merged_dict, unmerged_dictionaries 