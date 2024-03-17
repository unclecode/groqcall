
from phi.llm.openai.like import OpenAILike
from phi.assistant import Assistant
from phi.tools.duckduckgo import DuckDuckGo
import os, json


groq = OpenAILike(
        model="mixtral-8x7b-32768",
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
assistant = Assistant(
    llm=groq,
    tools=[DuckDuckGo()], show_tool_calls=True, markdown=True
)

# If you run without a proxy, you will get a error, becuase Groq does not have a function to call
# assistant.print_response("Whats happening in France? Summarize top stories with sources, very short and concise.", stream=False)

my_groq = OpenAILike(
        model="mixtral-8x7b-32768", # or model="gemma-7b-it",        
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://groqcall.ai/proxy/groq/v1" # or "http://localhost:8000/proxy/groq/v1" if running locally
    )
assistant = Assistant(
    llm=my_groq,
    tools=[DuckDuckGo()], show_tool_calls=True, markdown=True
)
assistant.print_response("Whats happening in France? Summarize top stories with sources, very short and concise.", stream=False)




