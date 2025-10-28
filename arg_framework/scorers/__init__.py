from abc import ABC as _ABC, abstractmethod as _abstractmethod

class Scorer(_ABC):
    @_abstractmethod
    def score_clue(self, clue=None, guess_colors=None, *kwargs) -> float:
        pass

    def game_start(self):
        pass
    def round_update(self, clue, guess_colors):
        pass
    def game_end(self):
        pass

from .__colt_scorer import ColtScorer
"""
3 Scorers

Win Ratio:
    My Card over total
    Who is winning

    Ex: 
    9 red 8 blue: 9/17   0.53
    -2 red -1 blue:   7/14   0.5   score = 0.03
    -2 red              5/12  0.42 score = 0.08
    -1 blue             5/11  0.45 score = -0.03

Win Time extrapolation:
    Integer feedback

"""