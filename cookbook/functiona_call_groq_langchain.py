# pip install --upgrade --quiet langchain-groq tavily-python langchain langchainhub langchain-openai

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()
from langchain import hub
from langchain.agents import create_openai_tools_agent
from langchain_community.tools.tavily_search import TavilySearchResults, TavilyAnswer
from langchain.agents import AgentExecutor

# The following code raise an error.
chat = ChatGroq(
    temperature=0, 
    groq_api_key=os.environ["GROQ_API_KEY"],
    model_name="mixtral-8x7b-32768", 
)

prompt = hub.pull("hwchase17/openai-tools-agent")
tools = [TavilySearchResults(max_results=1)]
agent = create_openai_tools_agent(chat, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, stream_runnable = False)
agent_executor.invoke({"input": "What is Langchain?"})


# The following code works fine using GroqCall (Funckycall) proxy
chat = ChatGroq(
    temperature=0, 
    groq_api_key=os.environ["GROQ_API_KEY"], 
    model_name="mixtral-8x7b-32768", 
    groq_api_base= "http://localhost:8000/proxy/groqchain"
    # groq_api_base= "http://groqcall.ai/proxy/groqchain"
)

# Example 1: Chat with tools
prompt = hub.pull("hwchase17/openai-tools-agent")
tools = [TavilySearchResults(max_results=1)]
agent = create_openai_tools_agent(chat, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, stream_runnable = False)
result = agent_executor.invoke({"input": "What is Langchain?"})
print(result)

# Example 1: Simple chat
system = "You are a helpful assistant."
human = "{text}"
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

chain = prompt | chat
result = chain.invoke({"text": "Explain the importance of low latency LLMs."})
print(result)
