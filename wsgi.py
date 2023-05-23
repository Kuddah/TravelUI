from app import app, set_agent_chain
from waitress import serve
from langchain.agents import AgentExecutor, LLMSingleActionAgent
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from llmchains import prompt, output_parser, tools


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
Flightchain = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True)
set_agent_chain(Flightchain)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8000)
    