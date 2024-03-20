from groq import Groq
from openai import OpenAI
from litellm import completion as sync_call_llm
import litellm


class BaseProvider:
    def __init__(self, api_key: str, base_url = None):
        self.api_key = api_key
        self.parser_model = ""
        self.route_model = ""

    def route(self, model: str, messages: list, **kwargs):
        pass

    async def route_async(self, model: str, messages: list, **kwargs):
        pass

    def clean_params(self, params):
        pass


class OpenaiProvider(BaseProvider):
    def __init__(self, api_key: str, base_url = None):
        super().__init__(api_key)
        self._client = OpenAI(api_key=api_key)
        self.parser_model = "gpt-3.5-turbo"
        self.route_model = "gpt-3.5-turbo"
        self.exclude_params = ["messages"]

    def route(self, model: str, messages: list, **kwargs):
        completion = self._client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return completion

    def clean_params(self, params):
        return {k: v for k, v in params.items() if k not in self.exclude_params}


class GroqProvider(BaseProvider):
    def __init__(self, api_key: str, base_url = None):
        super().__init__(api_key)
        self._client = Groq(api_key=api_key)
        self.parser_model = "mixtral-8x7b-32768"
        self.route_model = "mixtral-8x7b-32768"
        self.exclude_params = ["messages", "tools", "tool_choice"]
       
    def route(self, model: str, messages: list, **kwargs):
        completion =  self._client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return completion
    
    def clean_params(self, params):
        return {k: v for k, v in params.items() if k not in self.exclude_params}
        

class OllamaProvider(BaseProvider):
    def __init__(self, api_key: str, base_url = None):
        super().__init__(api_key)
        self.parser_model = "gemma:2b"
        self.route_model = "gemma:7b"
        self.exclude_params = ["messages", "tools", "tool_choice"]
        
    def route(self, model: str, messages: list, **kwargs):
        # Filter out all messages with rol assistant and has key "tool_calls"
        messages = [message for message in messages if message["role"] != "assistant" and "tool_calls" not in message]
        params = self.clean_params(kwargs)
        params = {
            'max_tokens': 2048,
            **params
        }
        response = sync_call_llm(
            model=f"ollama/{model}",
            api_base="http://localhost:11434",
            messages=messages,
            **self.clean_params(kwargs)
        )

        return response
    
    def clean_params(self, params):
        return {k: v for k, v in params.items() if k not in self.exclude_params}