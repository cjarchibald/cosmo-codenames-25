from langchain_community.chat_models import ChatOllama,ChatAnthropic,ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from .api_keys import GEMINI_API_KEY, GEMINI_BASE_URL, OLLAMA_BASE_URL, LOCAL_OLLAMA_BASE_URL
import requests
import os
import time
import random
import logging

#add relevent models/types as necessary throughout the project
class LangChainWrapper:
    def __init__(self, llm_type, model,  system_prompt, demo_input, demo_output, temp = 0.2, bad_demo_input = None, bad_demo_output = None):
        super().__init__()
        self.model_version = model
        self.sys_prompt = system_prompt
        self.demo_input = demo_input
        self.demo_output = demo_output
        self.bad_demo_input = bad_demo_input
        self.bad_demo_output = bad_demo_output
        if isinstance(demo_input, list) or bad_demo_input != None:
            self.init_hist_mult_demos()
        else:
            self.init_history()
        self.temperature = temp
        self.client = None
        #assuming user provides the correct type that corresponds to the model
        match llm_type.lower():
            case "gemini":
                #We still have to use the open ai compatibillity as lang chain does not offer gemini support
                api_key = GEMINI_API_KEY
                base_url = GEMINI_BASE_URL
                self.client = ChatOpenAI(model=model, openai_api_key = api_key, openai_api_base = base_url,temperature=self.temperature, max_tokens=5000)
            case "openai":
                #LangChain should automatically load and pass the env variables
                self.client = ChatOpenAI(model=model, temperature=self.temperature, max_tokens=5000)
            case "anthropic":
                self.client = ChatAnthropic(model=model, temperature=self.temperature, max_tokens=5000)
            case "ollama":
                #get the address of the computer we are running Ollama on
                if is_ollama_running(LOCAL_OLLAMA_BASE_URL):
                    base_url = LOCAL_OLLAMA_BASE_URL
                else:
                    base_url = OLLAMA_BASE_URL
                self.client = ChatOllama(model=model, base_url=base_url, temperature=self.temperature, max_tokens=5000)
            case _:
                logging.error("LLM not recognized")
        
    def prompt_ai_structured_output(self,prompt,structure):
        parser = PydanticOutputParser(pydantic_object=structure)
        #add formatting instructures to the end of the incoming prompt
        self.conversation_history.append({"role": "user", "content": "/no_think" + prompt +  parser.get_format_instructions()})
        raw_response = self.client.invoke(
            input=self.conversation_history
        )
        try:
            #use langchains parser to parse the raw json of the LLM output
            parsed_response = parser.parse(raw_response.content)
        except OutputParserException as e:
            #some models output thinking blocks so this code should find and cut out those blocks
            if raw_response.content.startswith('<think>'):
                end_index = raw_response.content.find('</think>')
                #splice out the thinking block (including the the tags)
                content_without_thinking = raw_response.content[end_index+8:]
                parsed_response = parser.parse(content_without_thinking)
            else:
                #otherwise delete the extra prompt, re raise the error so we can reprompt and try again
                self.conversation_history = self.conversation_history[:-1]
                if raw_response.content == "" :
                    raise OutputParserException("Empty response")
                raise OutputParserException(e)
        #add the response (in json form) to conversation history
        self.conversation_history.append({"role": "assistant", "content": parsed_response.json()})
        logging.info(parsed_response.json())
        return parsed_response
    
    #delay prompting idea from chatgpt
    def talk_to_ai(self, prompt, max_attempts=2, base_delay=12, expo_rate = 2, structure = None):
        attempts = 0
        while attempts < max_attempts:
            try:
                return self.prompt_ai_structured_output(prompt,structure)
            #we reprompt without bumping up the attempt count, this could lead to infinite loops
            except OutputParserException as e:
                if str(e) == "Empty response":
                    if isinstance(self.demo_input, list) or self.bad_demo_input != None:
                        self.init_hist_mult_demos()
                    else:
                        self.init_history()
                logging.warning(str(e))
                print("Parser error. Reprompting now")
                attempts += 1
            #ideally this should only catch the exceptions dealing with rate limits, model overload etc.    
            except Exception as e:
                #exponential decay method
                logging.warning(str(e))
                attempts += 1
                delay = base_delay + expo_rate * (2 ** attempts) + random.uniform(0, 1)
                print(f"Unable to connect to OLLAMA. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
        raise OutputParserException("Max attempts reached")

    def init_history(self):
        self.conversation_history = [{"role": "system", "content": self.sys_prompt}]
        #if we dont have both the demonstration examples we only keep system prompt
        if self.demo_input is not None and self.demo_output is not None:
            self.conversation_history.append({"role": "user", "content": self.demo_input})
            self.conversation_history.append({"role": "assistant", "content": self.demo_output})
    
    def init_hist_mult_demos(self):
        self.conversation_history = [{"role": "system", "content": self.sys_prompt}]
        if self.bad_demo_input != None:
            self.conversation_history.append({"role": "system", "content": (
                "Below are a few good examples of how to respond to the Codenames clue task.\n"
                "These are followed by a clearly marked bad example to avoid.\n"
                "Then you will be asked to generate a new answer."
                )})
        if isinstance(self.demo_input, list):
            for i in range(len(self.demo_input)): # This assumes that the indexing links up between demo inputs and outputs
                self.conversation_history.append({"role": "user", "content": self.demo_input[i]})
                self.conversation_history.append({"role": "assistant", "content": self.demo_output[i]})
        else:
            self.conversation_history.append({"role": "user", "content": self.demo_input})
            self.conversation_history.append({"role": "assistant", "content": self.demo_output})
        if self.bad_demo_input != None:
            if isinstance(self.bad_demo_input, list):
                for i in range(len(self.bad_demo_input)):
                    self.conversation_history.append({"role": "user", "content": "⚠️ Bad Example — do NOT do this:\n" + self.bad_demo_input[i]})
                    self.conversation_history.append({"role": "assistant", "content": self.bad_demo_output[i]})
            else:
                self.conversation_history.append({"role": "user", "content": "⚠️ Bad Example — do NOT do this:\n" + self.bad_demo_input})
                self.conversation_history.append({"role": "assistant", "content": self.bad_demo_output})
    
def is_ollama_running(base_url):
    try:
        response = requests.get(base_url, timeout=2)
        if response.status_code == 200:
            # print('Ollama is running locally!')
            return True
        else:
            # print('Ollama is Not running locally :(')
            return False
    except requests.exceptions.RequestException:
        return False