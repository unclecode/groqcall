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