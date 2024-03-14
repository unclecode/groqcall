# FunckyCall.ai
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1q3is7qynCsx4s7FBznCfTMnokbKWIv1F?usp=sharing)
[![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/unclecode/funckycall)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

FunckyCall is a proxy server provides function call for Groq's lightning-fast Language Processing Unit (LPU) and other AI providers. Additionally, the upcoming FuncyHub will offer a wide range of built-in functions, hosted on the cloud, making it easier to create AI assistants without the need to maintain function schemas in the codebase or or execute them through multiple calls.

## Motivation 🚀
Groq is a startup that designs highly specialized processor chips aimed specifically at running inference on large language models. They've introduced what they call the Language Processing Unit (LPU), and the speed is astounding—capable of producing 500 to 800 tokens per second or more. I've become a big fan of Groq and their community;


I admire what they're doing. It feels like after discovering electricity, the next challenge is moving it around quickly and efficiently. Groq is doing just that for Artificial Intelligence, making it easily accessible everywhere. They've opened up their API to the cloud, but as of now, they lack a function call capability.

Unable to wait for this feature, I built a proxy that enables function calls using the OpenAI interface, allowing it to be called from any library. This engineering workaround has proven to be immensely useful in my company for various projects. Here's the link to the GitHub repository where you can explore and play around with it. I've included some examples in this collaboration for you to check out.

<img width="150" src = "https://res.cloudinary.com/kidocode/image/upload/v1710148127/GroqChip-1-Die_lgi95d.jpg"/>

<img title="Powered by Groq" alt="Powered by Groq" width = "150" src="https://res.cloudinary.com/kidocode/image/upload/v1710142103/Stack_PBG_White_n6qdbj.svg">



## Running the Proxy Locally 🖥️
To run this proxy locally on your own machine, follow these steps:

1. Clone the GitHub repository:
```git clone https://github.com/unclecode/funckycall.git```

2. Navigate to the project directory:
```cd funckycall```

3. Create a virtual environment:
```python -m venv venv```

4. Install the required libraries:
```pip install -r requirements.txt```

5. Run the FastAPI server:
```uvicorn --app-dir app/ main:app --reload```


## Using the Pre-built Server 🌐
For your convenience, I have already set up a server that you can use temporarily. This allows you to quickly start using the proxy without having to run it locally.

To use the pre-built server, simply make requests to the following base URL:
```https://funckycall.ai/proxy/groq/v1```


## Exploring FunckyCall.ai 🚀
This README is organized into three main sections, each showcasing different aspects of FunckyCall.ai:

- **Sending POST Requests**: Here, I explore the functionality of sending direct POST requests to LLMs using FunckyCall.ai. This section highlights the flexibility and control offered by the library when interacting with LLMs.
- **FunckyHub**: The second section introduces the concept of FunckyHub, a useful feature that simplifies the process of executing functions. With FunckyHub, there is no need to send the function JSON schema explicitly, as the functions are already hosted on the proxy server. This approach streamlines the workflow, allowing developers to obtain results with a single call without having to handle function call is production server.
- **Using FunckyCall with PhiData**: In this section, I demonstrate how FunckyCall.ai can be seamlessly integrated with other libraries such as my favorite one, the PhiData library, leveraging its built-in tools to connect to LLMs and perform external tool requests.


```python
# The following libraries are optional if you're interested in using PhiData or managing your tools on the client side.
!pip install phidata > /dev/null
!pip install openai > /dev/null
!pip install duckduckgo-search > /dev/null
```

## Sending POST request, with full functions implementation 


```python
from duckduckgo_search import DDGS
import requests, os
import json

# Here you pass your own GROQ API key
api_key=userdata.get("GROQ_API_KEY")
header = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
proxy_url = "https://funckycall.ai/proxy/groq/v1/chat/completions"


def duckduckgo_search(query, max_results=None):
    """
    Use this function to search DuckDuckGo for a query.
    """
    with DDGS() as ddgs:
        return [r for r in ddgs.text(query, safesearch='off', max_results=max_results)]

def duckduckgo_news(query, max_results=None):
    """
    Use this function to get the latest news from DuckDuckGo.
    """
    with DDGS() as ddgs:
        return [r for r in ddgs.news(query, safesearch='off', max_results=max_results)]

function_map = {
    "duckduckgo_search": duckduckgo_search,
    "duckduckgo_news": duckduckgo_news,
}

request = {
    "messages": [
        {
            "role": "system",
            "content": "YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY.\n<instructions>\n1. Use markdown to format your answers.\n</instructions>"
        },
        {
            "role": "user",
            "content": "Whats happening in France? Summarize top stories with sources, very short and concise."
        }
    ],
    "model": "mixtral-8x7b-32768",
    "tool_choice": "auto",
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "duckduckgo_search",
                "description": "Use this function to search DuckDuckGo for a query.\n\nArgs:\n    query(str): The query to search for.\n    max_results (optional, default=5): The maximum number of results to return.\n\nReturns:\n    The result from DuckDuckGo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string"
                        },
                        "max_results": {
                            "type": [
                                "number",
                                "null"
                            ]
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "duckduckgo_news",
                "description": "Use this function to get the latest news from DuckDuckGo.\n\nArgs:\n    query(str): The query to search for.\n    max_results (optional, default=5): The maximum number of results to return.\n\nReturns:\n    The latest news from DuckDuckGo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string"
                        },
                        "max_results": {
                            "type": [
                                "number",
                                "null"
                            ]
                        }
                    }
                }
            }
        }
    ]
}

response = requests.post(
    proxy_url,
    headers=header,
    json=request
)
if response.status_code == 200:
    res = response.json()
    message = res['choices'][0]['message']
    tools_response_messages = []
    if not message['content'] and 'tool_calls' in message:
        for tool_call in message['tool_calls']:
            tool_name = tool_call['function']['name']
            tool_args = tool_call['function']['arguments']
            tool_args = json.loads(tool_args)
            if tool_name not in function_map:
                print(f"Error: {tool_name} is not a valid function name.")
                continue
            tool_func = function_map[tool_name]
            tool_response = tool_func(**tool_args)
            tools_response_messages.append({
                "role": "tool", "content": json.dumps(tool_response)
            })

        if tools_response_messages:
            request['messages'] += tools_response_messages
            response = requests.post(
                proxy_url,
                headers=header,
                json=request
            )
            if response.status_code == 200:
                res = response.json()
                print(res['choices'][0]['message']['content'])
            else:
                print("Error:", response.status_code, response.text)
    else:
        print(message['content'])
else:
    print("Error:", response.status_code, response.text)

```

## Schema-less Function Call 🤩
In this method, we only need to provide the function's name, which consists of two parts, acting as a sort of namespace. The first part identifies the library or toolkit containing the functions, and the second part specifies the function's name, assuming it's already available on the proxy server. I aim to collaborate with the community to incorporate all typical functions, eliminating the need for passing a schema. Without having to handle function calls ourselves, a single request to the proxy enables it to identify and execute the functions, retrieve responses from large language models, and return the results to us. Thanks to Groq, all of this occurs in just seconds.


```python
from duckduckgo_search import DDGS
import requests, os
api_key = userdata.get("GROQ_API_KEY")
header = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

proxy_url = "https://funckycall.ai/proxy/groq/v1/chat/completions"


request = {
    "messages": [
        {
            "role": "system",
            "content": "YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY.\n<instructions>\n1. Use markdown to format your answers.\n</instructions>",
        },
        {
            "role": "user",
            "content": "Whats happening in France? Summarize top stories with sources, very short and concise. Also please search about the histoy of france as well.",
        },
    ],
    "model": "mixtral-8x7b-32768",
    "tool_choice": "auto",
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "duckduck.search",
            },
        },
        {
            "type": "function",
            "function": {
                "name": "duckduck.news",
            },
        },
    ],
}

response = requests.post(
    proxy_url,
    headers=header,
    json=request,
)

if response.status_code == 200:
    res = response.json()
    print(res["choices"][0]["message"]["content"])
else:
    print("Error:", response.status_code, response.text)

```

## Using with PhiData
FindData is a favorite of mine for creating AI assistants, thanks to its beautifully simplified interface, unlike the complexity seen in the LangChain library and LlamaIndex. I use it for many projects and want to give kudos to their team. It's open source, and I recommend everyone check it out. You can explore more from this link https://github.com/phidatahq/phidata.


```python
from google.README import userdata
from phi.llm.openai.like import OpenAILike
from phi.assistant import Assistant
from phi.tools.duckduckgo import DuckDuckGo
import os, json


my_groq = OpenAILike(
        model="mixtral-8x7b-32768",
        api_key=userdata.get("GROQ_API_KEY"),
        base_url="https://funckycall.ai/proxy/groq/v1"
    )
assistant = Assistant(
    llm=my_groq,
    tools=[DuckDuckGo()], show_tool_calls=True, markdown=True
)
assistant.print_response("Whats happening in France? Summarize top stories with sources, very short and concise.", stream=False)


```

## Contributions Welcome! 🙌
I am excited to extend and grow this repository by adding more built-in functions and integrating additional services. If you are interested in contributing to this project and being a part of its development, I would love to collaborate with you! I plan to create a discord channel for this project, where we can discuss ideas, share knowledge, and work together to enhance the repository.

Here's how you can get involved:

1. Fork the repository and create your own branch.
2. Implement new functions, integrate additional services, or make improvements to the existing codebase.
3. Test your changes to ensure they work as expected.
4. Submit a pull request describing the changes you have made and why they are valuable.

If you have any ideas, suggestions, or would like to discuss potential contributions, feel free to reach out to me. You can contact me through the following channels:

- Twitter (X): @unclecode
- Email: unclecode@kidocode.com

### Copyright 2024 Unclecode (Hossein Tohidi)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

I'm open to collaboration and excited to see how we can work together to enhance this project and provide value to the community. Let's connect and explore how we can help each other!

Together, let's make this repository even more awesome! 🚀
