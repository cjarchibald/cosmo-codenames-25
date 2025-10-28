from ..experiment_settings import ExperimentSettings
from .. import file_paths

class BotSettingsObj:
    N_ASSOCIATIONS = None
    LOG_FILE = None
    LEARN_LOG_FILE_CM = None
    LEARN_LOG_FILE_G = None
    LEARNING_ALGORITHM = None
    INCLUDE_SAME_LM = None
    MODEL_PATH = None
    BOT_TYPE_SM = None  #lm of codemaster
    BOT_TYPE_G = None   #lm of guesser
    PRINT_LEARNING = None
    ENSEMBLE_PARAMS = None
    CONSTRUCTOR_PATHS = None
    EMBEDDING_NOISE = None
    DIST_NOISE = None
    DETECT = None
    AI_TYPE = None
    ANC_STRATEGY = None
    ANC_WEIGHT = None
    ANC_INIT_NOISE = None
    TEST_ID = None
    ANC_THRESH = None
    ANC_GAME_THRESH = None
    CM_STRATEGY = None
    G_STRATEGY = None
    SAMPLE_SIZE_G = None
    COLOR = None
    LLM_TYPE = None
    LLM_MODEL = None

def get_bot_settings(experiment_settings: ExperimentSettings):
    bot_settings = BotSettingsObj()
    bot_settings.N_ASSOCIATIONS = experiment_settings.n_associations
    bot_settings.ENSEMBLE_PARAMS = experiment_settings.ensemble_parameters
    if experiment_settings.noise_parameters is not None:
        bot_settings.EMBEDDING_NOISE, bot_settings.DIST_NOISE = experiment_settings.noise_parameters
    bot_settings.DETECT = experiment_settings.detect
    bot_settings.LEARNING_ALGORITHM = experiment_settings.learning_algorithm
    bot_settings.INCLUDE_SAME_LM = experiment_settings.include_same_lm
    bot_settings.MODEL_PATH = file_paths.model_path
    bot_settings.PRINT_LEARNING = experiment_settings.print_learning

    return bot_settings