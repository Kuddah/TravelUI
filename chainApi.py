from base import APIChain
import flightapi
from langchain.chat_models import ChatOpenAI
from amdeusapi import get_amadeus_token
import os
# from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
# from langchain.prompts.prompt import PromptTemplate

# _DEFAULT_TEMPLATE = """Given an input question, first create a syntactically
# correct {dialect} query to run, then look at the results of the 
# query and return the answer.
# Use the following format:

# Question: "Question here"
# SQLQuery: "SQL Query to run"
# SQLResult: "Result of the SQLQuery"
# Answer: "Final answer here"

# Only use the following tables:

# {table_info}
# no need to mention the flight id, and if thier is any stops, pls mention the 
# layovers information from the FlightSegments table



# Question: {input}"""
# PROMPT = PromptTemplate(
#     input_variables=["input", "table_info", "dialect"], 
#     template=_DEFAULT_TEMPLATE
# )

# db = SQLDatabase.from_uri("sqlite:///flights.db")
# llm = OpenAI(temperature=0)
# db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=PROMPT, verbose=True)


client_id = 'iApYXewA9W2JFPQggvjA46TsOSfV1fvb'
client_secret = 'ATEFOu6fmUGd79ki'


prompt = "Convert the destinationLocationCode and originLocationCodeto there respected IATA format"

os.environ['AMDEUS_BEARER_TOKEN'] = get_amadeus_token(client_id, client_secret)
headers = {"Authorization": f"Bearer {os.environ['AMDEUS_BEARER_TOKEN']}"}
llm = ChatOpenAI(temperature=0)

chain_new = APIChain.from_llm_and_api_docs(
    llm, flightapi.Flight_API, headers=headers, prompt=prompt, verbose=True)
