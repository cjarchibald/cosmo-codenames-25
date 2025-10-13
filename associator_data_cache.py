'''
This file will contain associations from the json file. You will pass in a filepath
'''
from .unknown_words_handler import UnknownWordsHandler
import json
__file_cache = dict()

def _pull_assocs_from_cache(filepath):
    if filepath not in __file_cache:
        with open(filepath) as f: __file_cache[filepath] = json.load(f).items()
    return __file_cache[filepath]


class AssociatorDataCache:
    def __init__(self, filepath):
        self.filepath = filepath
        self.associations = {}
        self.wordlist = []
        items = _pull_assocs_from_cache(self.filepath)
        items = dict(items)
        self.all_words = set(items.keys())
        self.all_words.update(set(w for assocs in items.values() for w in assocs))
    
    def load_cache(self,n):
        self.associations = {word:assocs[:n] for word, assocs, in _pull_assocs_from_cache(self.filepath)}
        self.wordlist = list(self.associations.keys())
    
    def get_ai_replacement(self, word):
        og_reverse_assoc_word = None
        og_closest_index = None
        word = word.lower()
        if word in self.associations.keys():
            return word
        if any(word in lst for lst in self.associations.values()):
            og_reverse_assoc_word, og_closest_index = self.get_reverse_association(word)
            return og_reverse_assoc_word
        synonyms = UnknownWordsHandler.get_ai_synonyms(word)
        for i in synonyms:
            if i in self.associations.keys():
                return i
        synonymDict = {}
        for i in synonyms:
            if any(i in lst for lst in self.associations.values()):
                closest_word, closest_index = self.get_reverse_association(i)
                synonymDict[closest_index] = closest_word
                
        # if og_reverse_assoc_word:
        #     synonymDict[og_closest_index] = og_reverse_assoc_word

        if bool(synonymDict):
            print("dict: ", synonymDict)
            lowest_index = min(synonymDict.keys())
            closest_word = synonymDict[lowest_index]
            return closest_word
        return 'error'
        
    
    def get_reverse_association(self, word):
        closest_key = None
        closest_index = float("inf")

        for key, values in self.associations.items():
            if word in values:
                index = values.index(word)
                if index < closest_index:
                    closest_index = index
                    closest_key = key
        return closest_key, closest_index


        
    # go through associations and find closest to root word, return root word as a synonym as that word.


    def get_associations(self, word):
        # if word not in self.associations:
        #     return UnknownWordsHandler.generate_ai_associations(self.all_words,self.associations,word)            
        return self.associations[word]
    
    def get_wordlist(self):
        return self.wordlist
    
    def __getitem__(self, word):
        return self.associations[word]
    
    def get_ext_associations(self, word):
        original_associations = self.associations[word]
        new_associations = set(original_associations)
    
        for w in original_associations:
            related_word_associations = self.associations[w]
            new_associations.add(related_word_associations[0])
            
        return list(new_associations)
