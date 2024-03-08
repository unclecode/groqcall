from duckduckgo_search import DDGS
import requests, os, json
api_key = os.environ["GROQ_API_KEY"]
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

function_map = {
    "duckduckgo_search": duckduckgo_search,
}

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
                "name": "duckduckgo_search",
                "description": "Use this function to search DuckDuckGo for a query.\n\nArgs:\n    query(str): The query to search for.\n    max_results (optional, default=5): The maximum number of results to return.\n\nReturns:\n    The result from DuckDuckGo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "max_results": {"type": ["number", "null"]},
                    },
                },
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
    headers= header,
    json=request,
)
# Check if the request was successful
if response.status_code == 200:
    # Process the response data (if needed)
    res = response.json()
    message = res["choices"][0]["message"]
    tools_response_messages = []
    if not message["content"] and "tool_calls" in message:
        if 'resolved' in res:
            # Append resolved message to the tools response messages
            tools_response_messages.extend(res['resolved'])

        for tool_call in message["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = tool_call["function"]["arguments"]
            tool_args = json.loads(tool_args)
            if tool_name not in function_map:
                print(f"Error: {tool_name} is not a valid function name.")
                continue
            tool_func = function_map[tool_name]
            tool_response = tool_func(**tool_args)
            tools_response_messages.append(
                {"role": "tool", "content": json.dumps(tool_response), "name": tool_name, "tool_call_id": tool_call["id"]}
            )

        if tools_response_messages:
            request["messages"] += tools_response_messages
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
    else:
        print(message["content"])
else:
    print("Error:", response.status_code, response.text)
