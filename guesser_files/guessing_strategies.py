from abc import abstractmethod
import random

from .bot_strategy import BotStrategy

# TODO refactor into several files?

class GuesserStrategies(BotStrategy):
    @abstractmethod
    def extra_guess(self, not_oppos: list, remains: list, round):
        pass


class DeducedOnly(GuesserStrategies):
    def extra_guess(self, not_oppos: list, remains: list, round):
        return None

class AlwaysGuess(GuesserStrategies):
    def extra_guess(self, not_oppos: list, remains: list, round):
        if len(not_oppos) > 0:
            return random.choice(not_oppos)
        else:
            return random.choice(remains)
        
class UnknownsSecondOnward(GuesserStrategies):
    def extra_guess(self, not_oppos: list, remains: list, round):
        if round > 2:
            return AlwaysGuess.extra_guess(not_oppos, remains, round)
        else:
            return None
        
# currently, add new strategies here