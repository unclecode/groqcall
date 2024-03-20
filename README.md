# GroqCall.ai - Lightning-Fast LLM Function Calls

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1q3is7qynCsx4s7FBznCfTMnokbKWIv1F?usp=sharing)
[![Version](https://img.shields.io/badge/version-0.0.4-blue.svg)](https://github.com/unclecode/groqcall)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

GroqCall is a proxy server that enables lightning-fast function calls for Groq's Language Processing Unit (LPU) and other AI providers. It simplifies the creation of AI assistants by offering a wide range of built-in functions hosted on the cloud.

## Quickstart

### Using the Pre-built Server

To quickly start using GroqCall without running it locally, make requests to one of the following base URLs:

- Cloud: `https://groqcall.ai/proxy/groq/v1`
- Local: `http://localhost:8000` (if running the proxy server locally)

### Running the Proxy Locally

1. Clone the repository:
```
git clone https://github.com/unclecode/groqcall.git
cd groqcall
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run the FastAPI server:
```
./venv/bin/uvicorn --app-dir app/ main:app --reload
```

## Examples

### Using GroqCall with PhiData

```python
from phi.llm.openai.like import OpenAILike
from phi.assistant import Assistant
from phi.tools.duckduckgo import DuckDuckGo

my_groq = OpenAILike(
    model="mixtral-8x7b-32768",
    api_key="YOUR_GROQ_API_KEY",
    base_url="https://groqcall.ai/proxy/groq/v1"  # or "http://localhost:8000/proxy/groq/v1" if running locally
)

assistant = Assistant(
    llm=my_groq,
    tools=[DuckDuckGo()], 
    show_tool_calls=True, 
    markdown=True
)

assistant.print_response("What's happening in France? Summarize top stories with sources, very short and concise.", stream=False)
```

### Using GroqCall with Requests

#### FuncHub: Schema-less Function Calls

GroqCall introduces FuncHub, which allows you to make function calls without passing the function schema. 

```python
import requests

api_key = "YOUR_GROQ_API_KEY"
header = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

proxy_url = "https://groqcall.ai/proxy/groq/v1/chat/completions" # or "http://localhost:8000/proxy/groq/v1/chat/completions" if running locally

request = {
    "messages": [
        {
            "role": "system",
            "content": "YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY.\n<instructions>\n1. Use markdown to format your answers.\n</instructions>"
        },
        {
            "role": "user", 
            "content": "What's happening in France? Summarize top stories with sources, very short and concise."
        }
    ],
    "model": "mixtral-8x7b-32768",
    "tool_choice": "auto",
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "duckduck.search"
            }
        },
        {
            "type": "function",
            "function": {
                "name": "duckduck.news"
            }
        }
    ]
}

response = requests.post(
    proxy_url,
    headers=header,
    json=request
)

print(response.json()["choices"][0]["message"]["content"])
```

- If you notice, the function schema is not passed in the request. This is because GroqCall uses FuncHub to automatically detect and call the function based on the function name in the cloud, Therefore you dont't need to parse the first response, call the function, and pass again. Check "functions" folder to add your own functions. I will create more examples in the close future to explain how to add your own functions.

#### Passing Function Schemas

If you prefer to pass your own function schemas, refer to the [Function Schema example](https://github.com/unclecode/groqcall/blob/main/cookbook/function_call_with_schema.py) in the cookbook.

#### Rune proxy with Ollama locally

Function call proxy can be used with Ollama. You should first install Ollama and run it locally. Then refer to the [Ollama example](https://github.com/unclecode/groqcall/blob/main/cookbook/function_call_ollama.py) in the cookbook.

## Cookbook

Explore the [Cookbook](https://github.com/unclecode/groqcall/tree/main/cookbook) for more examples and use cases of GroqCall.

## Motivation

Groq is a startup that designs highly specialized processor chips aimed specifically at running inference on large language models. They've introduced what they call the Language Processing Unit (LPU), and the speed is astounding—capable of producing 500 to 800 tokens per second or more.

As an admirer of Groq and their community, I built this proxy to enable function calls using the OpenAI interface, allowing it to be called from any library. This engineering workaround has proven to be immensely useful in my company for various projects.

## Contributing

Contributions are welcome! If you have ideas, suggestions, or would like to contribute to this project, please reach out to me on Twitter (X) @unclecode or via email at unclecode@kidocode.com.

Let's collaborate and make this repository even more awesome! 🚀

## License

This project is licensed under the Apache License 2.0. See [LICENSE](https://github.com/unclecode/groqcall/blob/main/LICENSE) for more information.