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
assistant.print_response("Whats happening in France? Summarize top stories with sources, very short and concise.", stream=False)

my_groq = OpenAILike(
        model="mixtral-8x7b-32768",
        api_key=os.environ["GROQ_API_KEY"],
        base_url="http://localhost:11235/proxy/groq/v1"
    )
assistant = Assistant(
    llm=my_groq,
    tools=[DuckDuckGo()], show_tool_calls=True, markdown=True
)
assistant.print_response("Whats happening in France? Summarize top stories with sources, very short and concise.", stream=False)

my_ollama = OpenAILike(
        model="gemma:7b",
        api_key="",
        base_url="http://localhost:11235/proxy/ollama/v1"
    )
ollama_assistant = Assistant(
    llm=my_ollama,
    tools=[DuckDuckGo()], show_tool_calls=True, markdown=True
)
ollama_assistant.print_response("Whats happening in France? Summarize top stories with sources, very short and concise.", stream=False)