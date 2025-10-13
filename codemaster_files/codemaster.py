import abc
from typing import Any
from ..bot_files.bot_settings_obj import BotSettingsObj
from ..enums import Color, GameCondition

class Codemaster(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def initialize(self, settings_obj: BotSettingsObj|Any):
        pass
    
    @abc.abstractmethod
    def load_dict(self, boardwords: list[str], first=None):
        pass
    
    @abc.abstractmethod
    def generate_clue(self, player_words, prev_clues, opponent_words, assassin_word, bystander_words)->tuple[str, list[str]]:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def give_feedback(self, guess: str, end_status: GameCondition, color: Color=None):
        pass

    def add_guess(self, guess: str):
        pass

    def send_start_sig(self):
        pass

    def send_end_sig(self):
        pass

    def inform_enemy_clue(self, clue_word, clue_num):
        pass