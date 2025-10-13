from .arg_framework.bot_files.bot_settings_obj import BotSettingsObj
from .codemaster import Codemaster
from .arg_framework.unknown_words_handler import UnknownWordsHandler
from .arg_framework.codemaster_files import codemaster as cm
from .arg_framework.codemaster_files.secret_competitive_codemaster import SecretCompetitiveCodemaster
from .arg_framework.codemaster_files.optimal_deducing_codemaster import Optimal_Deducing_Codemaster
from .arg_framework.associator_data_cache import AssociatorDataCache
from .arg_framework.enums import GameCondition, Color
import logging
from .arg_framework.__init__ import BotType
from .arg_framework.bot_files.bot_initializer import BotInitializer
from .arg_framework import file_paths
from .arg_framework.bot_files import bot_paths
import os


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodemasterWrapper(Codemaster):
    def __init__(self, team="Red", ai=BotType.COMPETITIVE_CODEMASTER, lm=BotType.CN_NB_DISTANCE_ASSOCIATOR, strategy=None, llmType = "ollama_seed", llmModel = "gemma3", logSynonyms = False, version = 'competitive'):
        if version == 'competitive':
            ai = BotType.SECRET_COMPETITIVE_CODEMASTER
        else:
            ai = BotType.OPTIMAL_DEDUCING_CODEMASTER
        self.team = team
        self.llm = llmType
        self.model = llmModel
        self.opponent = "Blue"
        if team == "Blue":
            self.opponent = "Red"

        self.log_synonyms = logSynonyms
        self.player_words = list()
        self.opponent_words = list()
        self.assassin_word = str
        self.bystander_words = list()
        self.board_words = list()
        self.prev_clues = list()
        self.original_board_words = list()
        if lm.value.split()[0] == 'glove':
            self.name = f'{ai.value.split()[0]} ({lm.value.split()[0]}-{lm.value.split()[1]})'
        else:
            self.name = f'{ai.value.split()[0]} ({lm.value.split()[0]})'
        bot_initializer = BotInitializer()
        settings = self.get_bot_settings(lm, strategy)
        #For the codemaster gpt bot
        if ai == BotType.GPT_CODEMASTER:
            settings.LLM_TYPE = llmType
            settings.LLM_MODEL = llmModel
            self.is_llm = True
        else:
            self.is_llm = False
        self.codemaster: cm.Codemaster = bot_initializer.init_bots(ai, None, settings)[0]
        self.prev_clue = ''
        self.board_is_set = False
        self.gave_feedback = list()
        if not self.is_llm:
            self.assoc_cache = AssociatorDataCache(settings.CONSTRUCTOR_PATHS[0])
            self.assoc_cache.load_cache(settings.N_ASSOCIATIONS)
            # Keep track of all potential clues and find illegal clues to ensure we do not use an illegal clue
            self.all_potential_clues = self.assoc_cache.all_words
            self.illegal_clues = set()
        self.move_history = None
        self.last_turn_history = None
        # used to reset the board if we guess wrong
        self.we_guessed_bad = False

    def set_game_state(self, words_on_board: list[str], key_grid: list[str]) -> None:
        self.words_remaining = words_on_board.copy()
        if not self.board_is_set:
            self.original_board_words = words_on_board.copy()
            if not self.is_llm:
                # print("ORIGINAL " + self.team.upper() + " CODEMASTER BOARD", self.original_board_words,"\n")
                # self.original_board_words = self.find_guessed_words(words_on_board.copy())
                self.board_words = self.get_board_replacements(self.original_board_words)
                # print("UPDATED " + self.team.upper() + " CODEMASTER BOARD",self.board_words,"\n")
                if self.log_synonyms:
                    with open("results/bot_results.txt", "a") as f:
                        f.write(f"UPDATED_{self.team.upper()}_CM_BOARD:{self.board_words} ")
            else:
                self.board_words = [word.lower() for word in words_on_board]
            self.codemaster.load_dict(self.board_words, self.team == "Red")
            self.board_is_set = True
        else:
            self.update_history(self.last_turn_history)
        # Regenerate the board words if we guessed incorrectly
        if self.we_guessed_bad and not self.is_llm:
            # print("ORIGINAL " + self.team.upper() + " CODEMASTER BOARD", self.original_board_words,"\n")
            self.board_words = self.get_board_replacements(self.original_board_words)
            # print("REUPDATED " + self.team.upper() + " CODEMASTER BOARD",self.board_words,"\n")
            if self.log_synonyms:
                with open("results/bot_results.txt", "a") as f:
                    f.write(f"REUPDATED_{self.team.upper()}_CM_BOARD:{self.board_words} ")
            self.codemaster.load_dict(self.board_words, self.team == "Red")
            self.gave_feedback.clear()

        try:
            self.player_words = []
            self.opponent_words = []
            self.bystander_words = []
            if len(self.gave_feedback) == 0:
                first_turn = True
            else:
                 first_turn = False
            for i in range(len(self.board_words)):

                if self.board_words[i] not in self.gave_feedback and self.original_board_words[i] not in words_on_board:
                    color = Color.ASSA
                    if words_on_board[i] == "*" + self.team + "*":
                        color = Color.TEAM
                    elif words_on_board[i] == "*" + self.opponent + "*":
                        color = Color.OPPONENT
                    elif words_on_board[i] == "*Civilian*":
                        color = Color.BYST

                    
                    # on the first turn just add the guesses because we havent init the different word types(should only matter for codemaster)
                    if first_turn:
                        self.codemaster.add_guess(self.board_words[i])
                        self.gave_feedback.append(self.board_words[i])
                    else:
                        self.codemaster.give_feedback(self.board_words[i], GameCondition.CONTINUE, color)
                        self.gave_feedback.append(self.board_words[i])

            for i in range(len(words_on_board)):

                # if not an already guessed word, add to the appropriate word list
                player_token = self.team
                opponent_token = self.opponent

                if words_on_board[i][0] != '*':
                    if key_grid[i] == player_token:
                        self.player_words.append(self.board_words[i])
                    elif key_grid[i] == opponent_token:
                        self.opponent_words.append(self.board_words[i])
                    elif key_grid[i] == 'Assassin':
                        self.assassin_word = self.board_words[i]
                    else:
                        self.bystander_words.append(self.board_words[i])       
        except Exception as e:
            logger.error(f"Failed to set game state: {e}")
            raise

    def get_original_word(self,word):
        return self.original_board_words[self.board_words.index(word)]

    def get_clue(self) -> tuple[str, int]:
        # Check for specific bots to see if we need to reset assumptions when we are wrong.
        if isinstance(self.codemaster,SecretCompetitiveCodemaster) or isinstance(self.codemaster,Optimal_Deducing_Codemaster):
            self.get_illegal_clues()
            results = self.codemaster.generate_clue(self.player_words, self.prev_clues, self.opponent_words,
                                                self.assassin_word, self.bystander_words, self.we_guessed_bad, self.illegal_clues)
        else:
            results = self.codemaster.generate_clue(self.player_words, self.prev_clues, self.opponent_words,
                                                self.assassin_word, self.bystander_words)
        clue, targets = results[0], results[1]
        targets = [self.get_original_word(target) for target in targets]
        # print("My Clue:", clue, targets)
        self.prev_clues.append(clue)
        if not clue or not targets:
            if clue and not targets:
                return (clue,0)
            logger.warning("No valid clue found, using fallback strategy")
            return ("", 1)
        tuple_result = (clue.upper(), len(targets))
        # logger.info(f"Generated clue: {tuple_result}")
        return tuple_result

    def get_board_replacements(self,words):
        
        if not self.we_guessed_bad:
            print(f'{self.team} Codemaster Analyzing Board...')
            return UnknownWordsHandler().get_ai_replacements(words,self.llm,self.model)
        # If we need to regenerate synonyms do a different seed
        else:
            return UnknownWordsHandler().get_ai_replacements(words,self.llm,self.model, seed=1234)

    def get_bot_settings(self, lm, strategy):
        bot_settings = BotSettingsObj()
        bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(lm)
        bot_settings.MODEL_PATH = file_paths.model_path
        bot_settings.CM_STRATEGY = strategy
        bot_settings.BOT_TYPE_SM = lm
        if self.team == 'Red':
            bot_settings.COLOR = Color.RED
        else:
            bot_settings.COLOR = Color.BLUE

        return bot_settings
    
    def set_move_history(self,move_history):
        if self.move_history is not None:
            self.last_turn_history = move_history[len(self.move_history):].copy()
        else:
            self.last_turn_history = move_history.copy()
        self.move_history = move_history.copy()

    def update_history(self,history):
        # loop through each event
        self.we_guessed_bad = False
        for event in history:
                # if it is a codemaster event and it is of the other team
            if "Codemaster" in event[0] and self.team not in event[0]:
                # inform guesser
                self.codemaster.inform_enemy_clue(event[1].lower(),event[2])
            # If we guessed a non-team word then set self.we_guessed_bad to True
            if 'Guesser' in event[0] and self.team in event[0] and self.team not in event[2]:
                self.we_guessed_bad = True

    def get_illegal_clues(self):
        from nltk.stem import SnowballStemmer, WordNetLemmatizer
        import nltk
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            import pronouncing
        
        
        nltk.download('wordnet', quiet=True)
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "arg_framework", "clue_blacklist.txt")
        with open(file_path, 'r') as f:
            black_list = [line.strip() for line in f if line.strip()]

        stemmer = SnowballStemmer('english')
        lemmatizer = WordNetLemmatizer()
        self.illegal_clues = set()
        current_board_words = []
        for word in self.words_remaining:
            if word[0] == '*':
                continue
            current_board_words.append(word.lower())
        for clue in self.all_potential_clues:
            illegal_clue = False
            for boardword in current_board_words:
                if boardword[0] == '*':
                    continue
                if clue in boardword or boardword in clue:
                    illegal_clue = True
                elif stemmer.stem(clue) == stemmer.stem(boardword):
                    illegal_clue = True
                elif lemmatizer.lemmatize(clue, 'v') == lemmatizer.lemmatize(boardword, 'v'):
                    illegal_clue = True
                elif clue in black_list:
                    illegal_clue = True
                elif len(pronouncing.phones_for_word(clue)) > 0:
                    clue_sound = pronouncing.phones_for_word(clue)
                    boardword_sound = pronouncing.phones_for_word(boardword)
                    shared_sound = set(clue_sound) & set(boardword_sound)
                    if shared_sound:
                        illegal_clue = True
                if illegal_clue:
                    self.illegal_clues.add(clue)
                    break
                
    