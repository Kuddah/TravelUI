from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI


db = SQLDatabase.from_uri("sqlite:///flights.db")
llm = OpenAI(temperature=0)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
prompt = "provid a table output format for every question asked"
FlightAgent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    prompt=prompt
)
