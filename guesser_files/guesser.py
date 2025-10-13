from abc import ABC, abstractmethod

from ..bot_files.bot_settings_obj import BotSettingsObj
from ..enums import Color, GameCondition


class Guesser(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def initialize(self, bot_settings_obj: BotSettingsObj):
        pass

    @abstractmethod
    def guess_clue(self, clue, num_guess, prev_guesses)->list[str]:
        raise NotImplementedError()

    @abstractmethod
    def load_dict(self, words: list[str], first=None):
        pass

    @abstractmethod
    def give_feedback(self, end_status: GameCondition, word_type: Color, word=None):
        pass

    def send_end_game_signal(self):
        pass

    def inform_enemy_clue(self, clue, num_to_guess):
        pass
    