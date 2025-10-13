from copy import deepcopy
from enum import IntEnum
# from play_games.bots.codemasters.adaptive_noise_codemaster import AdaptiveNoiseCodemaster
# from play_games.bots.codemasters.distance_associator_ai_codemaster import DistanceAssociatorAICodemaster
# from play_games.bots.codemasters.ensemble_ai_codemaster import EnsembleAICodemaster
# from play_games.bots.codemasters.noisy_distance_associator_codemaster import NoisyDistanceAssociatorAICodemaster
# from play_games.bots.codemasters.gpt_codemaster import gpt_codemaster
# from play_games.bots.guessers.ensemble_ai_guesser import EnsembleAIGuesser
# from play_games.bots.guessers.noisy_ai_guesser import  NoisyAIGuesser
from ..guesser_files.vector_baseline_guesser import VectorBaselineGuesser
# from play_games.bots.guessers.gpt_guesser import GptGuesser
# from play_games.bots.guessers.human_guesser import human_guesser




class BotConstructorType(IntEnum):

    VECTOR_BASELINE_CODEMASTER =               1, None
    ENSEMBLE_AI_CODEMASTER =                   2, None
    DISTANCE_ASSOCIATOR_AI_CODEMASTER =        3, None
    NOISY_DISTANCE_ASSOCIATOR_AI_CODEMASTER =  4, None
    NOISY_VECTOR_BASELINE_GUESSER =            5, None
    VECTOR_BASELINE_GUESSER =                  7, VectorBaselineGuesser
    ENSEMBLE_AI_GUESSER =                      8, None
    RANDOM_ENSEMBLE_AI_CODEMASTER =            9, None
    RANDOM_ENSEMBLE_AI_GUESSER =               10, None
    ADAPTIVE_NOISY_CODEMASTER =                11, None
    GPT_GUESSER =                              12, None
    HUMAN_GUESSER =                            13, None
    
    def __new__(cls, value, contr, *args, **kwargs):
        obj = int.__new__(cls)
        obj._value_ = value
        obj.constructor = contr
        return obj
    
    # def __init__(self, val, cls):
    #     pass

    def build(self, *args, **kwargs):
        if isinstance(self.constructor, type):
            return self.constructor(*args, **kwargs)
        else:
            return deepcopy(self.constructor)
