from ..associator_data_cache import AssociatorDataCache
from .clue_creator import *
from ..scorers import *
from ..bot_files.bot_settings_obj import BotSettingsObj
from .codemaster import Codemaster
from .. import BotType
from ..bot_files.bot_to_lm import get_lm
from ..experiment_settings import EnvFlag, is_true
from ..enums import Color, GameCondition
from ..typing_ import EndStatus, Word, WordList
from .. import utils as comp_utils
from .. import utils_play_games as utils
from typing import Dict,Tuple

class Optimal_Deducing_Codemaster(Codemaster):
    """This Codemaster looks at many of the possible ways to win in two turns, however there is a special assumption that is made.
    If a clue is given for 5 words then the 6th closest word to the clue can be assumed to not be a team word by both codemaster 
    and guesser. Thus that word can be ignored for the rest of the game. This assumption better helps the bot to win in 2 turns 
    even more often. 
    This bot is designed to work with the optimal_deducing_guesser and will fail if paired with a different bot."""

    _team_words: list[str]
    _oppo_words: list[str]
    _byst_words: list[str]
    _guesses_given: list[str]
    _assa_word = str
    _round = int
    _game = int

    def __init__(self, scorer=ColtScorer):
        self.scorer = scorer()
        self.clue_giver = OptimizedWithAssumptionClueGiver()
        self._guesses_given = []
        self._team_words = None
        self._oppo_words = None
        self._byst_words = None
        self._assa_word = None
        self._round = 0
        self._game = 0
        
    def initialize(self, settings_obj: BotSettingsObj):
        self._log_file = settings_obj.LEARN_LOG_FILE_CM
        self.lm_type = get_lm(settings_obj.BOT_TYPE_SM)
        self.vectors = VectorDataCache(settings_obj.CONSTRUCTOR_PATHS[1])
        self.associations = AssociatorDataCache(settings_obj.CONSTRUCTOR_PATHS[0])
        self.associations.load_cache(settings_obj.N_ASSOCIATIONS)
        self.round_weights = tuple(utils.load_joblib_no_warnings(settings_obj.MODEL_PATH).coef_)
        self.clue_giver.initialize(self.vectors, self.associations)
        self._initialize_scorer()

    def _initialize_scorer(self,):
        self.scorer.initialize(None, self.round_weights)

    def load_dict(self, boardwords: WordList, first=None):
        self.boardwords: list = boardwords.copy()
        self._on_game_started()
        self.clue_giver.load_clues(self.boardwords)
        

    def generate_clue(self, player_words: WordList, prev_clues: WordList, opponent_words: WordList, assassin_word: Word, bystander_words: WordList, reset_assumptions = False, illegal_clues = None):
        self._round += 1
        self._team_words = player_words
        self._oppo_words = opponent_words
        self._byst_words = bystander_words
        self._assa_word = assassin_word
        if illegal_clues:
            self.clue_giver.reload_clues(self.boardwords, illegal_clues)
        state = comp_utils.translate_words_to_colors(self.boardwords, player_words, opponent_words, bystander_words, assassin_word)
        self.clue_given = self.clue_giver.give_clue(state, self.boardwords, len(player_words), player_words, reset_assumptions)
        return self.clue_given
    
        
    def _log_clue(self, noise):
        self._log(
            f"Round: {self._round}\n"
            f"Noise: {noise}\n"
            f"Clue: {self.clue_given[0]} ; {self.clue_given[1]} ; {len(self.clue_given[1])}"
        )

    def give_feedback(self, guess: Word, end_status: EndStatus, color: Color=None):
        self.add_guess(guess)
        
        if color != Color.TEAM or len(self._guesses_given)==len(self.clue_given[1]):
            self._on_round_finished()
        
        if end_status != GameCondition.CONTINUE:
            self._on_game_ended(end_status)

    def add_guess(self, guess: Word):
        self._guesses_given.append(guess)
        self.boardwords.remove(guess)

    def _on_game_started(self):
        self._game += 1
        self.scorer.game_start()
        self._log(f"GAME STARTED: {self._game}")
        self._log("-"*20)

    def _on_round_finished(self):
        colors = comp_utils.translate_guesses_to_colors(self._guesses_given, self._team_words, self._oppo_words, self._byst_words, self._assa_word)
        reward = self.scorer.score_clue(self.clue_given, colors) 
        self._log_results(reward)
        
        self.scorer.round_update(self.clue_given, colors)
        self._guesses_given.clear()

    def _log_results(self, reward):
        self._log(
            f"Guesses: {self._guesses_given}\n"
            f"Reward: {reward}\n"
        )

    def _on_game_ended(self, end_status):
        self.scorer.game_end()
        match end_status:
            case GameCondition.WIN:
                self._log("GAME ENDED: WIN\n\n")
            case GameCondition.LOSS:
                self._log("GAME ENDED: LOSS\n\n")

    def _log(self, message, end='\n'):
        if self._log_file:
            self._log_file.write(f"{message}{end}")
        if is_true(EnvFlag.PRINT_LEARNING):
            print(message)

    def __desc__(self):
        return f"{BotType.COMPETITIVE_CODEMASTER}:{self.lm_type}"
    
    def send_start_sig(self):
        pass

    def send_end_sig(self):
        pass