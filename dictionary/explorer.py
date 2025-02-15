from typing import List
from .dictionary import Dictionary

class Explorer:
    """
    @brief Different ways to explore a dictionary
    """
    @staticmethod
    def sequences(dictionary: Dictionary, words: str, report):
        """
        @brief Determine if the words passed are valid sub-sequences of any
        word in the dictionary e.g. 'UZZL' is a valid sub-sequence in
        an English dictionary as it is found in 'PUZZLE', but 'UZZZL'
        isn't.
        @param dictionary dawg to explore
        @param words list of words to check
        @param report reporter function(word). This function
        will be called each time a matching word is found, passing the word
        as a string.
        """
        if not isinstance(dictionary, Dictionary):
            raise ValueError("Not a Dictionary")
        
        for word in words:
            if dictionary.has_sequence(word):
                report(word)
    
    @staticmethod
    def anagrams(dictionary: Dictionary, words: str, report: callable):
        """
        @brief Find anagrams of the words that use all the letters. `.`
        works as a character wildcard.
        @param dictionary dictionary dawg to explore
        @param words list of words to check
        @param report reporter function(word). This function
        will be called each time a matching word is found, passing the word
        as a string.
        """
        if not words or len(words) == 0:
            raise ValueError("Need letters to find anagrams of")

        for word in words:
            anagrams = dictionary.find_anagrams(word.replace('.', ' '))
            anagrams = [w for w in anagrams if len(w) == len(word)]
            for w in anagrams:
                report(w)
    
    @staticmethod
    def hangmen(dictionary: Dictionary, words: str, report: callable):
        """
        @brief Find words that hangman match all the letters. `.`
        works as a character wildcard.
        @param dictionary dawg to explore
        @param words list of words to check
        @param report reporter function(word). This function
        will be called each time a matching word is found, passing the word
        as a string.
        """
        if not words or len(words) == 0:
            raise ValueError("Need letters to find hangman matches for")

        for word in words:
            matches = dictionary.find_hangmen(word.replace('.', ' '))
            for w in matches:
                report(w)
    
    @staticmethod
    def arrangements(dictionary: Dictionary, words: str, report: callable):
        """
        @brief Find arrangements of the letters in the words e.g. `UIE` is a
        an arrangement of the letters in `QUIET`, as is `EIU` and `IUE`.
        @param dictionary dawg to explore
        @param words list of words to check
        @param report reporter function(word). This function
        will be called each time a matching word is found, passing the word
        as a string.
        """
        if not words or len(words) == 0:
            raise ValueError("Need letters to find arrangements of")

        for word in words:
            anagrams = dictionary.find_anagrams(word)
            for w in anagrams:
                report(w)
    
    @staticmethod
    def list(dictionary: Dictionary, words: List[str], report: callable):
        """
        @brief List all the words in the dictionary. If `words` is given,
        list all dictionary entries that start with one of the words.
        
        @param dictionary: dawg to explore
        @param words: list of words to check
        @param report: reporter function(word). This function
                       will be called once for each word in the dictionary.
        """
        if not words or len(words) == 0:
            dictionary.each_word(lambda word: report(word))
            return
        
        biglist = set()
        for word in words:
            word = word.upper()
            node = dictionary.match(word)
            if node:
                root = {'word': word, 'node': node}
                list_ = []
                biglist.add(root['word'])
                root['node'].child.eachWord(root['word'], lambda w: list_.append(w))

                list_ = [w for w in list_ if w not in biglist]
                for w in list_:
                    biglist.add(w)
                    report(w)
