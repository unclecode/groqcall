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


# '{"$defs": {"Choices": {"additionalProperties": true, "properties": {}, "title": "Choices", "type": "object"}, "StreamingChoices": {"additionalProperties": true, "properties": {}, "title": "StreamingChoices", "type": "object"}, "Usage": {"additionalProperties": true, "properties": {}, "title": "Usage", "type": "object"}}, "additionalProperties": true, "properties": {"id": {"title": "Id", "type": "string"}, "choices": {"items": {"anyOf": [{"$ref": "#/$defs/Choices"}, {"$ref": "#/$defs/StreamingChoices"}]}, "title": "Choices", "type": "array"}, "created": {"title": "Created", "type": "integer"}, "model": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "title": "Model"}, "object": {"title": "Object", "type": "string"}, "system_fingerprint": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "title": "System Fingerprint"}, "usage": {"anyOf": [{"$ref": "#/$defs/Usage"}, {"type": "null"}], "default": null}}, "required": ["id", "choices", "created", "object"], "title": "ModelResponse", "type": "object"}'