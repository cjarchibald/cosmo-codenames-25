from .. import utils

from . import Scorer

class ColtScorer(Scorer):
    def initialize(self, _, weights):
        self.weights=weights

    def score_clue(self, clue, guess_colors) -> float:
        match clue:
            case list() | tuple():
                clue_size = len(clue[1])
            case int():
                clue_size = clue

        return self.weights[utils.get_round_weight_idx(*utils.format_guesses(guess_colors, clue_size))]
