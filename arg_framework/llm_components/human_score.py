from .langchain_manager import LangChainWrapper
from . import prompts as prompts
from .human_interpretability_templates import Interpretability_Score, ClueConnection

class HumanInterpretabilityScore():
    def __init__(self,board:list[str]):
        self.board_words = []
        for word in board:
            self.board_words.append(word.lower())
        
    def update_board(self, updated_board: list[str]):
        self.board_words = []
        for word in updated_board:
            self.board_words.append(word.lower())
    def get_prompt_list(self):
        self.demo_input_list = []
        self.demo_output_list = []
        self.bad_demo_input_list = []
        self.bad_demo_output_list = []
        self.demo_input_list.append(prompts.WHALEhuman_rating_demo_input)
        self.demo_output_list.append(prompts.WHALE1human_rating_demo_output) #First human demo for whale clue
        self.demo_input_list.append(prompts.WHALEhuman_rating_demo_input)
        self.demo_output_list.append(prompts.WHALE2human_rating_demo_output) #Second human demo for whale clue
        self.demo_input_list.append(prompts.WHALEhuman_rating_demo_input)
        self.demo_output_list.append(prompts.WHALE3human_rating_demo_output) #Third human demo for whale clue
        self.demo_input_list.append(prompts.BOOThuman_rating_demo_input)
        self.demo_output_list.append(prompts.BOOThuman_rating_demo_output) #Boot clue example with only 1 misleading word
        self.demo_input_list.append(prompts.KITCHENhuman_rating_demo_input) 
        self.demo_output_list.append(prompts.KITCHENhuman_rating_demo_output) #kitchen clue example with 4 misleading words
        self.demo_input_list.append(prompts.VEALhuman_rating_demo_input)
        self.demo_output_list.append(prompts.VEAL_GOODhuman_rating_demo_output) #The Good veal example
        self.bad_demo_input_list.append(prompts.VEALhuman_rating_demo_input)
        self.bad_demo_output_list.append(prompts.VEAL_BADhuman_rating_demo_output) #The Bad veal example
        

    def get_human_interpretability_score(self,clue: str, targets: list[str],llm_type = "gemini",model = "gemini-2.5-flash"):
        bot = LangChainWrapper
        self.get_prompt_list()
        bot = bot(llm_type,model,prompts.human_rating_system_prompt, self.demo_input_list, self.demo_output_list, 0, self.bad_demo_input_list, self.bad_demo_output_list)
        # bot = bot(llm_type,model,prompts.human_rating_system_prompt,prompts.human_rating_demo_input,prompts.human_rating_demo_output,0)
        non_target_words = []
        targets = [word.lower() for word in targets]
        for word in self.board_words:
            if word.lower() not in targets:
                non_target_words.append(word.lower())
        response = bot.talk_to_ai(prompts.generate_human_score_prompt(self.board_words, clue, targets, non_target_words),structure = Interpretability_Score)
        total_HIS = 0
        total_clue_connection_score = 0
        for target in response.clue_connection:
            total_clue_connection_score += int(target.score)

        avg_clue_connection_score = total_clue_connection_score/len(response.clue_connection)
        total_HIS += avg_clue_connection_score
        total_HIS += response.theme_score
        total_HIS += response.cognitive_score
        total_HIS += response.clue_exclusivity_score
        with open('play_games/bots/ai_components/llm_components/HIS_Results.txt', 'a') as f:
            f.write(f'Board Words: {self.board_words}\n')
            f.write(f'Clue: {clue}\n')
            f.write(f'Target Words: {targets}\n')
            for target in response.clue_connection:
                f.write(f'   {target.target_word}: {target.score}. . . {target.analysis}\n')
            f.write(f'Connection Analysis: {response.connection_analysis}\n')
            f.write(f'Theme Score: {response.theme_score}. . . {response.theme_analysis}\n')
            f.write(f'Cognitive Score: {response.cognitive_score}. . . {response.cognitive_analysis}\n')
            f.write(f'Clue Exclusivity Score: {response.clue_exclusivity_score}. . . {response.clue_exclusivity_analysis}\n')
            f.write(f'Total Human Interpretability Score: {total_HIS}\n\n\n')
        # print(response)
        return total_HIS
    
