from ..vector_data_cache import VectorDataCache
from ..bot_files.bot_settings_obj import BotSettingsObj
from .guesser import Guesser


class Optimal_Deducing_Guesser(Guesser):
    """This guesser is designed to work with the Optimal_Deducing_Codemaster
    This looks at the clue, figures out the targets assuming both codemaster and guesser use the same lm
    It then looks one past the intended targets in terms of distance from clue and then makes the assumption that is not part of our words.
    """
    def __init__(self):
        self._ignore_words = set() #Any words definitely do not belong to our team
        pass

    def initialize(self, bot_settings_obj: BotSettingsObj):
        if isinstance(bot_settings_obj.CONSTRUCTOR_PATHS, (list, tuple)):
            self.vectors = VectorDataCache(*bot_settings_obj.CONSTRUCTOR_PATHS)
        else:
            self.vectors = VectorDataCache(bot_settings_obj.CONSTRUCTOR_PATHS)
        self.color = bot_settings_obj.COLOR # Extract color to know how many of our teamwords we need to get
            
    def guess_clue(self, clue, num_guess, prev_guesses, num_team_words_left = None, reset_assumptions = False):
        if reset_assumptions:
            self._ignore_words.clear()
        board_words = [w for w in self.board_words if w not in prev_guesses]
        if num_guess == 0:
            if num_team_words_left == None:
                num_team_words_left = 9
            return self._get_n_farthest_words(num_team_words_left, clue, board_words)
        return self._get_n_closest_words(num_guess, clue, board_words)

    def load_dict(self, words, first=None):
        
        if self.color == 'Red Team' or first == True:
            self.my_words_left = 9
        else:
            self.my_words_left = 8
        self._ignore_words = set()
        self.board_words = words.copy()
        
    def give_feedback(self, *_):
        pass

    def _get_n_closest_words(self, n, clue, words):
        sorted_words = sorted(words, key=lambda w: self.vectors.distance_word(clue, w))
        targets = []
        # Go through the sorted words closest to the clue picking the n closest that aren't on the ignore list
        for word in sorted_words:
            if word not in self._ignore_words:
                targets.append(word)
            if len(targets) == n:
                break
        # Loop through again and find the word we can ignore that is the next closest board word to the clue
        for word in sorted_words:
            if word not in targets and word not in self._ignore_words:
                self._ignore_words.add(word)
                break
        # print(f'guesser words to ignore: {self._ignore_words}')
        return targets
    
    def _get_n_farthest_words(self, n, clue, words):
        sorted_words = list(reversed(sorted(words, key=lambda w: self.vectors.distance_word(clue, w))))[:n]
        targets = []
        for word in sorted_words:
            if word not in self._ignore_words:
                targets.append(word)
            if len(targets) == n:
                break
        return targets