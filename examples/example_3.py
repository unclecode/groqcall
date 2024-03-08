from duckduckgo_search import DDGS
import requests, os
api_key = os.environ["GROQ_API_KEY"]
header = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
# proxy_url = "http://localhost:11235/proxy/groq/v1/chat/completions"
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
