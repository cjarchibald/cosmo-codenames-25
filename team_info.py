

from enum import IntEnum, StrEnum
from .ensemble_utils import LearningAlgorithms
from .codemaster_files.competitive_codemaster import CompetitiveCodemaster
from .guesser_files.guesser import Guesser
from . import BotType

#TODO refactor, factor TeamInfo, TeamColor, GameInfo, GameState, First, GameTrackings, ColtScorer into different file(s)

class TeamInfo():
    """Information about the team currently acting"""
    team_color = None
    current_cm: CompetitiveCodemaster = None
    current_guesser: Guesser = None
    codemaster_ai = None
    codemaster_lm = None
    guesser_ai = None
    guesser_lm = None
    
class TeamColor(StrEnum):
    """Enumeration that represents which team is currently acting"""
    RED = "Red Team"
    BLUE = "Blue Team"

class GameInfo():
    def __init__(self):
        self.current_active: TeamColor = None
        self.red_team_words: list[str] = None
        self.blue_team_words: list[str] = None
        self.byst_words: list[str] = None
        self.assassin: str = None
        self.board: list[str] = None
        self.pass_team_words: list[str] = None
        self.pass_opponent_words: list[str] = None
        self.red_prev_guesses: list[str] = None
        self.blue_prev_guesses: list[str] = None
        self.pass_prev_guesses: list[str] = None
        self.all_prev_guesses: list[str] = []
        self.red_turns: int = 0
        self.blue_turns: int = 0
        self.red_game_scores: list[float] = []
        self.blue_game_scores: list[float] = []
        self.assassin_hit = False
    
class GameState(StrEnum):
    RED = "RED WON"
    BLUE = "BLUE WON"
    ROUND_END = "NONE"

class First(IntEnum):
    RED = 0
    BLUE = 1
    RANDOM = 2
    ALTERNATE = 3

class StartCompGameInfo(): # config file on itself
    # All ai or lm are BotType
    # Change at some point...
    codemaster_ai_list = []
    codemaster_lm_list = []
    guesser_ai_list = []
    guesser_lm_list = []
    
    # Red Team Information
    codemaster_red_ai = None
    codemaster_red_lm = None
    codemaster_strategy_red = None
    guesser_red_ai = None
    guesser_red_lm = None
    guesser_strategy_red = None


    # Blue Team Information
    codemaster_blue_ai = None
    codemaster_blue_lm = None
    codemaster_strategy_blue = None
    guesser_blue_ai = None
    guesser_blue_lm = None
    guesser_strategy_blue = None
    
    # Game information
    games_to_play = 1
    keep_teams = True
    seed = None
    goes_first = First.RANDOM
    solo_game = False

    print_games = True
    log_games = False
    log_file = None

    # Ensemble information (for both sides)
    include_same_lm = False
    learning_algorithm = LearningAlgorithms.T4
    ensemble_params = .4

    # Other info
    n_associations = 300
    num_samples = None
    embedding_noise = 0.0
    dist_noise = 0.2
    score_colt = True
    llm_type = None
    llm_model = None

    def convert_bot_to_string(self, bot: BotType):
        match bot:
            case BotType.D2V_BASELINE_GUESSER | BotType.D2V_DISTANCE_ASSOCIATOR:
                return "d2v"
            case BotType.W2V_BASELINE_GUESSER | BotType.W2V_DISTANCE_ASSOCIATOR:
                return "w2v"
            case BotType.W2V_GLOVE_BASELINE_GUESSER | BotType.W2V_GLOVE_DISTANCE_ASSOCIATOR:
                return "w2v_glove"
            case BotType.GLOVE_50_BASELINE_GUESSER | BotType.GLOVE_50_DISTANCE_ASSOCIATOR:
                return "glove_50"
            case BotType.GLOVE_100_BASELINE_GUESSER | BotType.GLOVE_100_DISTANCE_ASSOCIATOR:
                return "glove_100"
            case BotType.GLOVE_200_BASELINE_GUESSER | BotType.GLOVE_200_DISTANCE_ASSOCIATOR:
                return "glove_200"
            case BotType.GLOVE_300_BASELINE_GUESSER | BotType.GLOVE_300_DISTANCE_ASSOCIATOR:
                return "glove_300"
            case BotType.CN_NB_BASELINE_GUESSER | BotType.CN_NB_DISTANCE_ASSOCIATOR:
                return "cn_nb"
            case BotType.FAST_TEXT_BASELINE_GUESSER | BotType.FAST_TEXT_DISTANCE_ASSOCIATOR:
                return "fast_text"
            case BotType.ELMO_BASELINE_GUESSER | BotType.ELMO_DISTANCE_ASSOCIATOR:
                return "elmo"
            case BotType.BERT1_BASELINE_GUESSER | BotType.BERT1_DISTANCE_ASSOCIATOR:
                return "bert1"
            case BotType.BERT2_BASELINE_GUESSER | BotType.BERT2_DISTANCE_ASSOCIATOR:
                return "bert2"
            
    def string_to_codemaster_bot(self, string: str):
        match string:
            case "d2v":
                return BotType.D2V_DISTANCE_ASSOCIATOR
            case "w2v":
                return BotType.W2V_DISTANCE_ASSOCIATOR
            case "w2v_glove":
                return BotType.W2V_GLOVE_DISTANCE_ASSOCIATOR
            case "glove_50":
                return BotType.GLOVE_50_DISTANCE_ASSOCIATOR
            case "glove_100":
                return BotType.GLOVE_100_DISTANCE_ASSOCIATOR
            case "glove_200":
                return BotType.GLOVE_200_DISTANCE_ASSOCIATOR
            case "glove_300":
                return BotType.GLOVE_300_DISTANCE_ASSOCIATOR
            case "cn_nb":
                return BotType.CN_NB_DISTANCE_ASSOCIATOR
            case "fast_text":
                return BotType.FAST_TEXT_DISTANCE_ASSOCIATOR
            case "elmo":
                return BotType.ELMO_DISTANCE_ASSOCIATOR
            case "bert1":
                return BotType.BERT1_DISTANCE_ASSOCIATOR
            case "bert2":
                return BotType.BERT2_DISTANCE_ASSOCIATOR
            case _:
                return None
            
    def string_to_guesser_bot(self, string: str):
        match string:
            case "d2v":
                return BotType.D2V_BASELINE_GUESSER
            case "w2v":
                return BotType.W2V_BASELINE_GUESSER
            case "w2v_glove":
                return BotType.W2V_GLOVE_BASELINE_GUESSER
            case "glove_50":
                return BotType.GLOVE_50_BASELINE_GUESSER
            case "glove_100":
                return BotType.GLOVE_100_BASELINE_GUESSER
            case "glove_200":
                return BotType.GLOVE_200_BASELINE_GUESSER
            case "glove_300":
                return BotType.GLOVE_300_BASELINE_GUESSER
            case "cn_nb":
                return BotType.CN_NB_BASELINE_GUESSER
            case "fast_text":
                return BotType.FAST_TEXT_BASELINE_GUESSER
            case "elmo":
                return BotType.ELMO_BASELINE_GUESSER
            case "bert1":
                return BotType.BERT1_BASELINE_GUESSER
            case "bert2":
                return BotType.BERT2_BASELINE_GUESSER
            case _:
                return None
            
    def first_string(self):
        match self.goes_first:
            case First.BLUE:
                return "blue"
            case First.RED:
                return "red"
            case First.ALTERNATE:
                return "alternate"
            case First.RANDOM:
                return "random"


#track things for the game, wins, scores, starts, etc.
class GameTrackings():
    red_wins = 0
    blue_wins = 0
    assassins = 0
    red_starts = 0
    blue_starts = 0
    blue_good_guess = 0 # blue gives an extra guess, and actually gets it
    red_fast_win = 0 # red wins in two turns and starts
    red_deduction = 0
    red_score = 0
    red_rounds = 0
    blue_score = 0
    blue_rounds = 0
    red_win_time = 0
    blue_win_time = 0
    red_countable_wins = 0
    blue_countable_wins = 0
    special_count = 0
    wins_in_3_turns = 0
    wins_in_2_turns = 0
    wins_in_1_turn = 0
    win_in_3_seeds = []

class ColtScorer():
    # s0100: float = -4.695
    # s0010: float = -1.854
    # s0001: float = -9.740
    # s1000: float = 1.706
    # s1100: float = -1.637
    # s1010: float = 0.007
    # s1001: float = -5.551
    # s2000: float = 1.941
    # s2100: float = -0.404
    # s2010: float = 0.830
    # s2001: float = -4.567
    # s3000: float = 2.274
    # s3100: float = 0.492
    # s3010: float = 1.468
    # s3001: float = -3.798
    # s4000: float = 2.712
    # s4100: float = 1.109
    # s4010: float = 1.945
    # s4001: float = -2.892
    # s5000: float = 3.022
    # s5100: float = 1.608
    # s5010: float = 1.960
    # s5001: float = -2.732
    # s6000: float = 2.960
    # s6100: float = 1.792
    # s6010: float = 2.129
    # s6001: float = -2.573
    # s7000: float = 2.950
    # s7100: float = 1.881
    # s7010: float = 2.110
    # s7001: float = -1.806
    # s8000: float = 2.444
    # s8100: float = 1.120
    # s8010: float = 1.296
    # s8001: float = -1.136
    # s9000: float = 1.528
    
    score_vector = [-4.695, -1.854, -9.740, 1.706, -1.637, 0.007, -5.551, 1.941, -0.404, 0.830, -4.567, 2.274, 0.492,
                    1.468, -3.798, 2.712, 1.109, 1.945, -2.892, 3.022, 1.608, 1.960, -2.732, 2.960, 1.792, 2.129,
                    -2.573, 2.950, 1.881, 2.110, -1.806, 2.444, 1.120, 1.296, -1.136, 1.528]

    def __init__(self):
        pass

    def initialize(self):
        pass

    def get_score(self, team_words, oppo_guessed=False, byst_guessed=False, assa_guessed=False):
        return self.score_vector[-1 + 4 * team_words + oppo_guessed + 2*byst_guessed + 3*assa_guessed]