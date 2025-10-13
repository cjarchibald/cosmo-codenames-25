
from .llm_components.langchain_manager import LangChainWrapper
from .llm_components.ollama_manager import OllamaClient
from .llm_components import prompts as prompts
from .unknown_words_handler_templates import WordList
import os
from pathlib import Path
import logging
class UnknownWordsHandler:
    def get_ai_synonyms(self,word,llm_type, model, seed = 42):
        if llm_type == 'ollama_seed':
            bot = OllamaClient
            bot = bot(llm_type,model,prompts.synonym_guru_system_prompt,prompts.synonym_guru_demo_input,prompts.synonym_guru_demo_output,0)
            response = bot.talk_to_ai(prompts.generate_synonym_guru_prompt(word),structure = WordList, seed=seed)
        else:
            bot = LangChainWrapper
            bot = bot(llm_type,model,prompts.synonym_guru_system_prompt,prompts.synonym_guru_demo_input,prompts.synonym_guru_demo_output,0)
            response = bot.talk_to_ai(prompts.generate_synonym_guru_prompt(word),structure = WordList)
        synonyms = response.word_list
        return synonyms
    
    def retry(self,word, llm_type , model):
        bot = LangChainWrapper
        if llm_type == 'ollama_seed':
            bot = OllamaClient
        else:
            bot = LangChainWrapper
        bot = bot(llm_type,model,prompts.word_expert_system_prompt,prompts.word_expert_demo_input,prompts.word_expert_demo_output,0)
        response = bot.talk_to_ai(prompts.generate_word_expert_prompt(word),structure=WordList)
        synonyms = response.word_list
        return synonyms
    
    def get_ai_replacements(self, words,llm_type = "gemini_seed",model = "gemini-2.0-flash-lite", seed = 42):
        # logging.info("Starting synonym generation!")

        # get root of project directory
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "actual-final-wl.txt")
        
        #read the file into a vocab list
        with open(file_path,'r') as f:
            vocab_list = f.read().splitlines()
        replacement_list = [None for _ in words]

        # first loop, add all the known words 
        for i in range(len(words)):
            current_word = words[i].lower()
            if current_word in vocab_list:
                    replacement_list[i] = current_word
                    # logging.info(f"Skipping over the word {current_word}")
            #check for plural but eventually a detailed checking function would be good checking for s, ed, ing
            if current_word.endswith('s') and current_word[:-1] in vocab_list:
                 current_word = current_word[:-1]

        #add replacements
        for i in range(len(words)):
            current_word = words[i]
            if replacement_list[i] is None:
                synonyms = self.get_ai_synonyms(current_word,llm_type,model, seed)
                j = 0
                retry = False
                while j < len(synonyms):
                    current_synonym = synonyms[j].lower()
                    #check for plural
                    if current_synonym.endswith('s') and current_synonym[:-1] in vocab_list:
                        current_synonym = current_synonym[:-1]
                    if current_synonym in vocab_list and current_synonym not in replacement_list:
                        replacement_list[i] = current_synonym
                        # logging.info(f"Appending the word {current_synonym} in place of {current_word}")
                        break
                       #if we hit the last element in the last try retry method once
                    elif current_synonym == synonyms[-1]:
                        if not retry:
                            # logging.info(f"Using retry method for {current_word}.")
                            synonyms.extend(self.retry(current_word,llm_type,model))
                            retry = True
                        else:
                            #if all fails add the fallback word 
                            # logging.info(f"No replacements found for {current_word}. Using fallback")
                            replacement_list[i] = ("fallback")
                    
                    j+=1
        return replacement_list
        
            
            