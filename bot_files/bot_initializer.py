from ..codemaster_files.secret_competitive_codemaster import SecretCompetitiveCodemaster
from ..codemaster_files.competitive_codemaster import CompetitiveCodemaster
from ..codemaster_files.optimal_deducing_codemaster import Optimal_Deducing_Codemaster
from ..guesser_files.optimal_deducing_guesser import Optimal_Deducing_Guesser
from ..guesser_files.secret_guesser import SecretGuesser
from .bot_settings_obj import BotSettingsObj
from .constructor import BotConstructorType
from .. import AIType, BotType
from . import bot_paths
from .bot_to_ai import get_ai

#TODO Refactor for ease

class BotInitializer():
    def __init__(self):
        self.orig_alg = None

    '''
    We use the ai_type to determine the constructor we need because each constructor is built for a specific ai_type and the filepaths determine which lm is used. 
    If we simply used the bot_type to determine which constructor to call, we would have a lot more conditional blocks and/or conditions. 
    '''
    def init_bots(self, bot_type_1: BotType, bot_type_2: BotType, bot_settings: BotSettingsObj):
        codemaster_bot = None
        guesser_bot = None
        if self.orig_alg == None: self.orig_alg = bot_settings.LEARNING_ALGORITHM #assign this if it is the first time it is called

        if bot_type_1 != None:

            bot_ai_type = get_ai(bot_type_1)
            bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type_1)

            match bot_ai_type:
                case AIType.COMPETITIVE:
                    codemaster_bot = self.initialize_competitive_cm(bot_settings)
                case AIType.OPTIMAL_DEDUCING:
                    codemaster_bot = self.initialize_optimal_deducing_codemaster(bot_settings)
                case AIType.SECRET_COMPETITIVE:
                    codemaster_bot = self.initialize_secret_competitive_codemaster(bot_settings)
                case _:
                    print("Error loading codemaster")
                    return

            codemaster_bot.initialize(bot_settings)

        if bot_type_2 != None:

            bot_ai_type = get_ai(bot_type_2)
            bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type_2)

            match bot_ai_type:
                case AIType.BASELINE:
                    guesser_bot = BotConstructorType.VECTOR_BASELINE_GUESSER.build()
                case AIType.OPTIMAL_DEDUCING:
                    guesser_bot = self.initialize_optimal_deducing_guesser(bot_settings)
                case AIType.SECRET:
                    guesser_bot = self.initialize_secret_guesser(bot_settings)
                case _:
                    print("Error loading guesser")
                    return 
            guesser_bot.initialize(bot_settings)

        return codemaster_bot, guesser_bot
    
    def initialize_competitive_cm(self, bot_settings: BotSettingsObj):
        bot_type = bot_settings.BOT_TYPE_SM
        bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type)
        return CompetitiveCodemaster()
    
    def initialize_optimal_deducing_codemaster(self, bot_settings: BotSettingsObj):
        bot_type = bot_settings.BOT_TYPE_SM
        bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type)
        return Optimal_Deducing_Codemaster()
    
    def initialize_optimal_deducing_guesser(self, bot_settings: BotSettingsObj):
        bot_type = bot_settings.BOT_TYPE_G
        bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type)
        return Optimal_Deducing_Guesser()

    def initialize_secret_competitive_codemaster(self, bot_settings: BotSettingsObj):
        bot_type = bot_settings.BOT_TYPE_SM
        bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type)
        return SecretCompetitiveCodemaster()

    def initialize_secret_guesser(self, bot_settings: BotSettingsObj):
        bot_type = bot_settings.BOT_TYPE_G
        bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type)
        return SecretGuesser()