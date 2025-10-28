import enum
from enum import StrEnum

class GameCondition(enum.IntEnum):
    """Enumeration that represents the different states of the game"""
    CONTINUE = 0
    LOSS = 1
    WIN = 2

class Color(enum.IntEnum):
    TEAM = 0
    OPPONENT = 1

    RED = 0
    BLUE = 1
    BYST = 2
    ASSA = 3

class ConfigKeys(StrEnum):
    N_GAMES = "n_games"
    N_ASSOCIATIONS = "n_associations"
    BOARD_SIZE = "board_size"
    TOURNAMENT_SETTING = "tournament_setting"
    CODEMASTERS = "codemasters"
    GUESSERS = "guessers"
    EXPERIMENT_TYPE = "experiment_type"
    CUSTOM_ROOT_NAME = "custom_root_name"
    LEARNING_ALGORITHM = "learning_algorithm"
    IS_PARAMETER_OPTIMIZATION = "is_parameter_optimization"
    CURR_ITERATION = "curr_iteration"
    ITERATION_RANGE = "iteration_range"
    INCLUDE_SAME_LM = "include_same_lm"
    CONVERGENCE_THRESHOLD = "convergence_threshold"
    ENSEMBLE_PARAMETERS = "ensemble_parameters"
    NOISE_PARAMETERS = "noise_parameters"
    ANC_PARAMETERS = "anc_parameters"
    DETECT = "detect"
    INDEPENDENT_VARIABLE = "independent_variable"
    VARIABLE_SPACE = "variable_space"
    VERBOSE_FLAG = "verbose_flag"
    PRINT_BOARDS = "print_boards"
    PRINT_LEARNING = "print_learning"

class ExperimentType(StrEnum):
    ANC_LEARNING_EXPERIMENT = "anc learning experiment"
    LEARNING_EXPERIMENT = "learning experiment"
    ANC_PARAMETER_EXPERIMENT = "anc parameter experiment"
    PARAMETER_EXPERIMENT = "parameter experiment"
    RANDOM_TOURNAMENT = "random tournament"
    RANDOM_SWEEP_TOURNAMENT = "random sweep tournament"
    TOURNAMENT = "tournament"

class Parameters(StrEnum):
    N_ASSOCIATIONS = "Number of Associations"

class IndependentVariables(StrEnum):
    N_ASSOCIATIONS = ConfigKeys.N_ASSOCIATIONS
    ENSEMBLE_PARAMETERS = ConfigKeys.ENSEMBLE_PARAMETERS
    NOISE_PARAMETERS = ConfigKeys.NOISE_PARAMETERS
    BASE = "base"
    DELTA = "delta"
    HOO = "hoo"
    STEP = "step"
    PERCENT = "percent"