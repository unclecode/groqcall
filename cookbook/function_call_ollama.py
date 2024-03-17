
from phi.llm.openai.like import OpenAILike
from phi.assistant import Assistant
from phi.tools.duckduckgo import DuckDuckGo

# Tried the proxy with Ollama and it works great, meaning we can use it with any provider. But, you never get the speed of Groq ;)
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