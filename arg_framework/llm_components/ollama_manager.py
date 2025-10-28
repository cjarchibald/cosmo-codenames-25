# Adapted from Quinn Karpowitz's LLM bot branch
from ollama import Client
from ollama import generate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from .langchain_manager import is_ollama_running
from .api_keys import OLLAMA_BASE_URL, LOCAL_OLLAMA_BASE_URL
import os
import time
import random
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
class OllamaClient:
    def __init__(self,llm_type, model, system_prompt, demo_input, demo_output, temp):
        """
        Initializes the OllamaClient with the target API URL and model type.
        
        :param base_url: The API endpoint for the Ollama model.
        :param llm_type: The LLM model type to use (from LLMType enum).
        """
        if is_ollama_running(LOCAL_OLLAMA_BASE_URL):
            self.base_url = LOCAL_OLLAMA_BASE_URL
        else:
            self.base_url = OLLAMA_BASE_URL
        self.model = model
        self.temperature = temp
        self.sys_prompt = system_prompt
        self.demo_input = demo_input
        self.demo_output = demo_output
        self.init_history()

    def prompt_ai_structured_output(self,prompt,structure, seed = 42):
        parser = PydanticOutputParser(pydantic_object=structure)
        client = Client(
            host=self.base_url
        )
        self.conversation_history.append({"role": "user", "content": "/no_think" + prompt})
        response = client.chat(model=self.model, messages=
            self.conversation_history, format=structure.model_json_schema()
        , options={
            "temperature":self.temperature,
            "top_p": 1.0,
            "repeat_penalty": 1.0,
            "seed": seed
            })

        completion_text = response["message"]["content"]
        response_obj = structure.model_validate_json(completion_text)
        completion_text
        self.conversation_history.append({"role": "assistant", "content": completion_text})
        # logging.info(completion_text)
        return response_obj
    
    #delay prompting idea from chatgpt
    def talk_to_ai(self, prompt, max_attempts=5, base_delay=12, expo_rate = 2, structure = None, seed = 42):
        attempts = 0
        while attempts < max_attempts:
            try:
                return self.prompt_ai_structured_output(prompt,structure, seed)
            #we reprompt without bumping up the attempt count, this could lead to infinite loops
            except OutputParserException as e:
                logging.warning(str(e))
                print("Parser error. Reprompting now")
            #ideally this should only catch the exceptions dealing with rate limits, model overload etc.    
            except Exception as e:
                #exponential decay method
                logging.warning(str(e))
                attempts += 1
                delay = base_delay + expo_rate * (2 ** attempts) + random.uniform(0, 1)
                print(f"Hit rate limit. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)

    def init_history(self):
        self.conversation_history = [{"role": "system", "content": self.sys_prompt}]
        #if we dont have both the demonstration examples we only keep system prompt
        if self.demo_input is not None and self.demo_output is not None:
            self.conversation_history.append({"role": "user", "content": self.demo_input})
            self.conversation_history.append({"role": "assistant", "content": self.demo_output})