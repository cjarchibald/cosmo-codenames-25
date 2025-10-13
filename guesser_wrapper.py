from .arg_framework.unknown_words_handler import UnknownWordsHandler
from .arg_framework.bot_files.bot_settings_obj import BotSettingsObj
from .arg_framework.guesser_files.secret_guesser import SecretGuesser
from .arg_framework import BotType,AIType
from .arg_framework import file_paths
from .arg_framework.bot_files import bot_paths
from .arg_framework.enums import Color
from .arg_framework.team_info import GameState
from .arg_framework.bot_files.bot_initializer import BotInitializer
from .arg_framework.bot_files.bot_to_lm import get_lm, getBotDict
from .arg_framework.bot_files.bot_to_ai import get_ai
from .arg_framework.guesser_files.guessing_strategies import *

class GuesserWrapper():
    def __init__(self,team = "Red",ai=BotType.CN_NB_BASELINE_GUESSER, lm=BotType.CN_NB_BASELINE_GUESSER, strategy=DeducedOnly,llmType = "ollama_seed",llmModel = "gemma3", logSynonyms=False, version='competitive'):
        if version == 'competitive':
            ai = BotType.SECRET_GUESSER
        else:
            ai = BotType.OPTIMAL_DEDUCING_GUESSER
        self.updated_boardwords = None
        self.associations = {}
        self.llm = llmType
        self.model = llmModel
        self.log_synonyms=logSynonyms
        self.clue = None
        self.old_boardwords = None
        self.guesses = []
        self.clue_num = 0
        self.move_history = None
        self.teamColor = team
        if self.teamColor == 'Red':
            self.team_words_left = 9
        else:
            self.team_words_left = 8
        if lm.value.split()[0] == 'glove':
            self.name = f'{ai.value.split()[0]} ({lm.value.split()[0]}-{lm.value.split()[1]})'
        else:
            self.name = f'{ai.value.split()[0]} ({lm.value.split()[0]})'
        self.last_turn_history = None
        #manually initialize bots
        bot_initializer = BotInitializer()
        settings = self.get_bot_settings(lm, strategy)
        #Set the settings for the guesser gpt bot
        if ai == BotType.GPT_GUESSER:
            settings.LLM_TYPE = llmType
            settings.LLM_MODEL = llmModel
            self.is_llm = True
        else:
            self.is_llm = False
        self.guesser = bot_initializer.init_bots(None, ai, settings)[1]
        self.prev_guesses = set()
        self.we_guessed_bad = False

    def set_board(self,words):
        if self.updated_boardwords is None:
            self.old_boardwords = words.copy()
            if not self.is_llm:
                # self.old_boardwords = self.find_guessed_words(self.old_boardwords)
                self.updated_boardwords = self.replace_unknown_board_words(self.old_boardwords)
            else:
                self.updated_boardwords = [word.lower() for word in words]
            self.guesser.load_dict(self.updated_boardwords.copy(),self.teamColor == "Red")
        else:
            self.update_history(self.last_turn_history)
        # If we guess bad then we want to regenerate the synpnyms
        if self.we_guessed_bad and not self.is_llm:
            previous_guesses_indexes = []
            for word in self.prev_guesses:
                og_word = self.get_original_word(word)
                previous_guesses_indexes.append(self.old_boardwords.index(og_word.upper()))
            self.updated_boardwords = self.replace_unknown_board_words(self.old_boardwords)
            self.prev_guesses.clear()
            for index in previous_guesses_indexes:
                self.prev_guesses.add(self.updated_boardwords[index])
            
    
    def set_clue(self,clue,num_guesses):
        # print(f'This is the clue I passed in {clue}')
        self.clue = clue
        #if we are not a llm type bot check to see if we have the clue word in our associations
        if not self.is_llm:
            known_clue = self.replace_unknown_word(clue,self.updated_boardwords)
            self.clue = known_clue
        # print(f"This is the clue i am using: {self.clue}")
        self.guesses = []
        self.clue_num = num_guesses

    def get_answer(self):
        # check to see if we havent made any guesses this round
        if self.guesses == [] and self.clue_num != 0:
            if isinstance(self.guesser, SecretGuesser):
                self.guesses = self.guesser.guess_clue(self.clue,self.clue_num,self.prev_guesses, num_team_words_left=self.team_words_left, reset_assumptions=self.we_guessed_bad)
            else:
                self.guesses = self.guesser.guess_clue(self.clue,self.clue_num,self.prev_guesses)
        if self.clue_num == 0:
            if isinstance(self.guesser, SecretGuesser):
                self.guesses = self.guesser.guess_clue(self.clue,0,self.prev_guesses, num_team_words_left=self.team_words_left, reset_assumptions=self.we_guessed_bad)
            else:
                self.guesses = self.guesser.guess_clue(self.clue,0,self.prev_guesses)
        # print(f"answers we want to guess: {[self.get_original_word(guess) for guess in self.guesses]}")
        #return the top element and pop it off the list
        ans = self.guesses.pop(0)
        self.prev_guesses.add(ans)

        # return original board word if we are using the llm layer 
        if not self.is_llm:
            return self.get_original_word(ans)
        return ans
    
    # keep guessing while we have more guesses
    def keep_guessing(self):
        return len(self.guesses) > 0
    
    # I am assuming that the codemaster will be using the same lm as the guesser when we use competitive ai
    # of course that doesnt work either because we need the bot that is the codemaster type to get the right file types

    def get_bot_settings(self,lm,strategy):
        bot_settings = BotSettingsObj()
        bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(lm)
        bot_settings.MODEL_PATH = file_paths.model_path
        bot_settings.G_STRATEGY = strategy
        if strategy != None:
            bot_settings.BOT_TYPE_SM = self.search_for_compatible_cm(lm)
        bot_settings.BOT_TYPE_G = lm
        # hardcode sample size at 1000 for now
        bot_settings.SAMPLE_SIZE_G = 1000
        return bot_settings
    
    #for the strategies that require an internal model of the codemaster this will choose a equivalent associator
    def search_for_compatible_cm(self,lm):
        botDict = getBotDict()
        for bot in botDict.keys():
            # if the bot has the same lm and it is a distance associator return it
            if get_lm(lm) == botDict[bot] and get_ai(bot) == AIType.DISTANCE_ASSOCIATOR:
                return bot
            
    def replace_unknown_board_words(self,board_words):
        #first add all the words we know first
        # print("GUESSER " + self.teamColor.upper() + "  ORIGINAL BOARD: ", board_words)
        if not self.we_guessed_bad:
            print(f'{self.teamColor} Guesser Analyzing Board...')
            updated_words = UnknownWordsHandler().get_ai_replacements(board_words,self.llm,self.model)
            # print("GUESSER " + self.teamColor.upper() + " UPDATED AI BOARD: ", updated_words)
        else:
            updated_words = UnknownWordsHandler().get_ai_replacements(board_words,self.llm,self.model, seed=1234)
            # print("GUESSER " + self.teamColor.upper() + " REUPDATED AI BOARD: ", updated_words)
        if self.log_synonyms:
            with open("results/bot_results.txt", "a") as f:
                if self.we_guessed_bad:
                    f.write(f"REUPDATED_{self.teamColor.upper()}_G_BOARD:{updated_words} ")
                else:
                    f.write(f"UPDATED_{self.teamColor.upper()}_G_BOARD:{updated_words} ")
        return updated_words
    
    def get_original_word(self,word):
        return self.old_boardwords[self.updated_boardwords.index(word)]

    def get_converted_word(self,word):
        return self.updated_boardwords[self.old_boardwords.index(word.upper())]
    
    def replace_unknown_word(self,word,updated_words):
        word = word.lower()
        if word[0] == "*":
            return word
        updated_words.append(word)
        #pretend like its the 26th board word
        return UnknownWordsHandler().get_ai_replacements(updated_words,self.llm, self.model)[-1]
    
    def set_move_history(self,move_history):
        if self.move_history is not None:
            self.last_turn_history = move_history[len(self.move_history):].copy()
        else:
            self.last_turn_history = move_history.copy()
        self.move_history = move_history.copy()
    
    def update_history(self,history):
        self.we_guessed_bad = False
        # loop through each event
        for event in history:
            # check if it is guesser or codemaster
            if "Guesser" in event[0]:
                if not self.is_llm:
                    converted_word = self.get_converted_word(event[1])
                else:
                    converted_word = event[1]
                self.prev_guesses.add(converted_word.lower())
                color = self.get_color_result(event[2])
                self.guesser.give_feedback(GameState.ROUND_END,color,converted_word)
                if self.teamColor in event[2]:
                    self.team_words_left -= 1
            
            # If we guessed a non-team word then set self.we_guessed_bad to True
            if 'Guesser' in event[0] and self.teamColor in event[0] and self.teamColor not in event[2]:
                self.we_guessed_bad = True

                # if it is a codemaster event and it is of the other team
            elif "Codemaster" in event[0] and self.teamColor not in event[0]:
                # inform guesser
                self.guesser.inform_enemy_clue(event[1].lower(),event[2])

    def get_color_result(self,result):
        colorString = ""
        colorType = None
        match result:
            case "*Red*":
                colorString = "Red"
            case "*Blue*":
                colorString = "Blue"
            case "*Civilian*":
                colorString = "Neutral"
                colorType = Color.BYST
            case "*Assasin*":
                colorString = "Neutral"
                colorType = Color.ASSA
        if colorString != "Neutral":
            if self.teamColor != colorString:
                colorType = Color.OPPONENT
            else:
                colorType = Color.TEAM
        return colorType
            

          

                    


    