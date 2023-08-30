import os

from langchain.chat_models import ChatOpenAI

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import load_prompt
from langchain.schema import BaseOutputParser


OPENAI_SECRET_KEY = os.environ.get('OPENAI_SECRET_KEY')
MODEL_NAME = 'gpt-4'
MODEL_TEMPERATURE = 1.2

SYSTEM_THOUGHT = load_prompt('thought.yaml')
SYSTEM_RESPONSE = load_prompt('response.yaml')

class MyChain:

    def __init__(self, llm=None, verbose=True,
                 openai_secret_key=OPENAI_SECRET_KEY):
        self.llm = llm
        if not self.llm:
            self.llm = ChatOpenAI(model_name=MODEL_NAME,
                                  temperature=MODEL_TEMPERATURE,
                                  openai_api_key=openai_secret_key)
        self.verbose = verbose
        self.output_parser = ListParser()

        human_template = '{human_input}'
        human_message_prompt = \
            HumanMessagePromptTemplate.from_template(human_template)

        # Init thought chain
        self.system_thought = \
            SystemMessagePromptTemplate(prompt=SYSTEM_THOUGHT)
        self.thought_memory = ConversationBufferMemory(
            memory_key='thought_history',
            return_messages=True)
        thought_prompt = ChatPromptTemplate.from_messages([
            self.system_thought,
            MessagesPlaceholder(variable_name='thought_history'),
            human_message_prompt])
        self.thought_chain = LLMChain(
            llm=self.llm,
            prompt=thought_prompt,
            memory=self.thought_memory,
            verbose=self.verbose)
        # Init response chain
        self.system_response = \
            SystemMessagePromptTemplate(prompt=SYSTEM_RESPONSE)
        self.response_memory = ConversationBufferMemory(
            memory_key='response_history',
            input_key='human_input',
            return_messages=True)
        response_prompt = ChatPromptTemplate.from_messages([
            self.system_response,
            MessagesPlaceholder(variable_name='response_history'),
            human_message_prompt])
        self.response_chain = LLMChain(
            llm=self.llm,
            prompt=response_prompt,
            memory=self.response_memory,
            verbose=self.verbose)
    
    def think(self, human_input):
        return self.thought_chain.predict(human_input=human_input)

    def respond(self, human_input, thought):
        return self.response_chain.predict(human_input=human_input,
                                           thought=thought)

    def interact(self, human_input):
        thought = self.think(human_input)
        response = self.respond(human_input, thought)
        questions = self.output_parser.parse(response)
        return questions


class ListParser(BaseOutputParser):

    def parse(self, text):
        return text.strip().split("\n")
