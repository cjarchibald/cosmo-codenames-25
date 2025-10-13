from ..vector_data_cache import VectorDataCache
from ..bot_files.bot_settings_obj import BotSettingsObj
from .guesser import Guesser
from .vector_baseline_guesser import VectorBaselineGuesser
from ..enums import Color
from ..team_info import TeamColor


# This bot does the exact same thing as the vector baseline, but guesses only one clue at a time unless it can win the game.
# This assumes that the codemaster has the same language model, and should be paired with its partner codemaster so that it isn't given clues that target a repeat word


class SecretGuesser(VectorBaselineGuesser):
    def __init__(self):
        super().__init__()
        self.my_words = []
        self.color = Color.RED
        self.num_words = 9
        self.use_assumptions = True # NOTE!!!!! Change this to true if you want to use assumptions, make sure you change the secret competetive codemaster to use the same value

    def load_dict(self, words, first=None):
        if self.use_assumptions:
            self._ignore_words = set()
        self.first_turn = True
        self.my_words = []
        return super().load_dict(words)

    def initialize(self, bot_settings_obj: BotSettingsObj):
        if bot_settings_obj.COLOR is not None:
            color = bot_settings_obj.COLOR
            if color == TeamColor.BLUE:
                self.color = Color.BLUE
                self.num_words = 8
        if isinstance(bot_settings_obj.CONSTRUCTOR_PATHS, (list, tuple)):
            self.vectors = VectorDataCache(*bot_settings_obj.CONSTRUCTOR_PATHS)
        else:
            self.vectors = VectorDataCache(bot_settings_obj.CONSTRUCTOR_PATHS)

    def guess_clue(self, clue, num_guess, prev_guesses, num_team_words_left = None, reset_assumptions = False):
        if reset_assumptions:
                self.my_words.clear()
        if self.use_assumptions:
            if reset_assumptions:
                self._ignore_words.clear()
            board_words = [w for w in self.board_words if w not in self.my_words and w not in prev_guesses and w not in self._ignore_words]
        else:
            board_words = [w for w in self.board_words if w not in self.my_words and w not in prev_guesses]

        if num_guess == 0 and self.first_turn:
            return self._get_n_farthest_words(self.num_words, clue, board_words)
        if num_guess == 0 and not self.first_turn: # Joey added this so if this breaks it is his fault
            if num_team_words_left == None:
                guesses = self._get_n_farthest_words(self.num_words - len(self.my_words), clue, board_words)
            else:
                guesses = self._get_n_farthest_words(num_team_words_left, clue, board_words)
            self.my_words.extend(guesses)
            return [x for x in self.my_words if x not in prev_guesses]
        self.first_turn = False
        if num_team_words_left == None:
            guess_once = len(self.my_words) + num_guess < self.num_words
        else:
            guess_once = num_guess != num_team_words_left
        if guess_once:
            guesses = self._get_n_closest_words(num_guess, clue, board_words)
            if self.use_assumptions:
                self.get_ignore_word(num_guess,clue, board_words)
            self.my_words.extend(guesses)

            return [guesses[0]]
        else:
            guesses = self._get_n_closest_words(self.num_words - len(self.my_words), clue, board_words)
            self.my_words.extend(guesses)

            return [x for x in self.my_words if x not in prev_guesses]

    def give_feedback(self, end_status, word, color=None):
        pass

    def _get_n_closest_words(self, n, clue, words):
        return sorted(words, key=lambda w: self.vectors.distance_word(clue, w))[:n]

    def _get_n_farthest_words(self, n, clue, words):
        return list(reversed(sorted(words, key=lambda w: self.vectors.distance_word(clue, w))))[:n]
    
    def get_ignore_word(self, n, clue, words):
        sorted_list = sorted(words, key=lambda w: self.vectors.distance_word(clue, w))
        self._ignore_words.add(sorted_list[n])
