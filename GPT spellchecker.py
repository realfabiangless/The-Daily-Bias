from pyairtable import Api, Base, Table
from time import sleep
import json
from langchain.chains import LLMChain, SequentialChain
from langchain.chat_models import ChatOpenAI
import tiktoken
import openai
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

#openai vars  
orgKey  = "org-3JQu0K94U1KbORZ0YZ4Ck7RV"
apiKey = "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"
completion_model = 'gpt-4'

#airtabel vars
airtable_api_key = 'patoU8CMCcKYFffVG.56d4c133868eec8102685208259678e69d13dc4a6895cdd9391f47dfea0a878a'
base_id = "appi16jkg9KC8ZlHG"
table_name = "Production Pipeline"

#count length of words in tokens
def tiktoken_len(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(
        text,
        disallowed_special=(),
    )
    return len(tokens)

#prompt templates
system_template=("You are a grammar and spelling checker. You are given a text, a language and suggestions from the software tool languagetool.org what could be mistakes. Your job is to output a text free of grammar or spelling mistakes")

system_message_prompt = SystemMessagePromptTemplate.from_template(system_template) 

task = "Look at the text, the language and the suggestions from another grammaer and spelling checker software. The output of that tool is in JSON format. The suggestions are not always correct. Sometimes the tool does not know of places, people or fiction characters and will suggest a spelling mistake where there is none. Make sure to just change the things that you think are actual nmistakes. Output a text free of grammar or spelling mistakes." 

human_template = task + "TEXT: {text}\nLANGUAGE: {language}\nSUGGESTIONS: {suggestions}\n"

human_message_prompt = HumanMessagePromptTemplate.from_template(human_template,input_variables=['text','language','suggestions'])

chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

#initialize chain
chat = ChatOpenAI(temperature=0,openai_api_key=apiKey,model_name=completion_model)

chain = LLMChain(llm=chat, prompt=chat_prompt, output_key = "chain_answer")

#get data from airtable
table = Table(airtable_api_key, base_id, table_name)

formula = "NOT({LanguageToolFeedback} = '')"

for records in table.iterate(page_size=1, max_records=20, formula=formula):
    print(records[0]['id'])
    text = records[0]['fields']['Main Content']
    language = "en-US"
    suggestions = records[0]['fields']['LanguageToolFeedback']
    correction = chain.run({"text": text, "language": language, "suggestions": suggestions})
    table.update(records[0]['id'], {"Main Content corrected": correction})