import requests, os

api_key = os.environ["GROQ_API_KEY"]
header = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

proxy_url = "https://groqcall.ai/proxy/groq/v1/chat/completions"  # or "http://localhost:8000/proxy/groq/v1/chat/completions" if running locally
proxy_url = "http://localhost:8000/proxy/groq/v1/chat/completions"

request = {
    "messages": [
        {
            "role": "system",
            "content": "YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY.\n<instructions>\n1. Use markdown to format your answers.\n</instructions>",
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://res.cloudinary.com/kidocode/image/upload/v1710690498/Gfp-wisconsin-madison-the-nature-boardwalk_m9jalr.jpg"
                    },
                },
            ],
        },
        {
            "role": "user",
            # "content": "What’s in this image?",
            "content": "Generate 3 keywords for the image description",
        },
    ],
    "model": "mixtral-8x7b-32768"
}

response = requests.post(proxy_url, headers=header, json=request)


response.text

print(response.json()["choices"][0]["message"]["content"])
