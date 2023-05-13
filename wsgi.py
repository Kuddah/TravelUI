from app import app, set_agent_chain
from waitress import serve
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.agents import AgentOutputParser
from langchain.prompts import BaseChatPromptTemplate
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from chainApi import chain_new
from sqlagent import FlightAgent
from llmchain import Flightchain
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, HumanMessage
import re


# Set up the chat model
# Define which tools the agent can use to answer user queries
APIchain = chain_new
FlightAgent = FlightAgent
tools = [
    Tool(
        name="AmadeusAgent",
        func=APIchain.run,
        description="useful for when you need to get the Flight information, the output will be saved in flights.db, convert the city name to IATAcode, currency should be in USD, max=30",
        return_direct=True
    ),    
    Tool(
        name="FlightAgent",
        func=FlightAgent.run,
        description="useful for to be used after getting the API response from the FlightAPI, to get the Flight information, after using the FlightAPI tool",
        return_direct=True
    ),
]
# Set up the base template
template = """Complete the objective as best you can. your task is to check the AmadeusAgent and find out all the input requirment to do the call the API. then 
get the information from the user, dont forget to use IATA code when using the API, 
You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

These were previous tasks you completed:



Begin!

Question: {input}
{agent_scratchpad}"""

# Set up a prompt template
class CustomPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]
    
    def format_messages(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)]
    
prompt = CustomPromptTemplate(
template=template,
tools=tools,
# This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
# This includes the `intermediate_steps` variable because that is needed
input_variables=["input", "intermediate_steps"]
)

# Set up the chat model
class CustomOutputParser(AgentOutputParser):
    
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},log=llm_output,
                )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)


output_parser = CustomOutputParser()
llm = ChatOpenAI(temperature=0)
# LLM chain consisting of the LLM and a prompt
llm_chain = LLMChain(llm=llm, prompt=prompt)
tool_names = [tool.name for tool in tools]
agent = LLMSingleActionAgent(
    llm_chain=llm_chain, 
    output_parser=output_parser,
    stop=["\nObservation:"], 
    allowed_tools=tool_names
)
Flightchain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
set_agent_chain(Flightchain)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8000)