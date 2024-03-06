from fastapi import FastAPI, HTTPException, APIRouter, Response, Request, Path
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Response
from groq import Groq
from ..prompts import SYSTEM_MESSAGE, CLEAN_UP_MESSAGE, SUFFIX, get_func_result_guide
import json, uuid

router = APIRouter()

# Add get endpoint for /openai/v1 and print request body
@router.get("/openai/v1")
async def get_openai_v1(response: Response):
    return {"message": "OpenAI v1 GET endpoint"}


@router.post("/{provider}/v1/chat/completions")
async def post_chat_completions(request: Request, provider: str = Path("openai", title="Provider")) -> JSONResponse:    
    try:
        api_token = request.headers.get("Authorization").split("Bearer ")[1]
        client = Groq(api_key=api_token)
        body = await request.json()
        print(json.dumps(body, indent=4))
  
        if "tools" in body and body['messages'][-1]['role'] == "user":
            messages = body["messages"]
            messages = [f"{m['role'].title()}: {m['content']}" for m in messages if m['role'] != "system"]
            tools = body["tools"]
            tools = [t['function'] for t in tools]
            tools = json.dumps(tools, indent=4)
            new_messages = [
                {
                    "role": "system",
                    "content": SYSTEM_MESSAGE
                },
                {
                    "role": "system",
                    "content": f"Conversation History:\n{''.join(messages)}\n\nTools: \n{tools}\n\n{SUFFIX}"
                }
            ]

            tries = 5
            while tries > 0:
                completion = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=new_messages,
                    temperature=0,
                    max_tokens=1024,
                    top_p=1,
                    stream=False,
                    stop=None,
                )

                try:
                    response = completion.choices[0].message.content
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0]
                    tool_response = json.loads(response)

                    tool_calls = []
                    for func in tool_response['tool_calls']:
                        tool_calls.append({
                            "id": f"call_{func['name']}_{uuid.uuid4()}",
                            "type": "function",
                            "function": {
                                "name": func['name'],
                                "arguments": json.dumps(func['arguments'])
                            }
                        })


                    break
                except Exception as e:
                    new_messages.append({
                        "role": "user",
                        "content": f"Error: {e}.\n\n{CLEAN_UP_MESSAGE}"
                    })

                    tries -= 1
                    continue

            if tries == 0:
                return JSONResponse(content={"tool_calls": []}, status_code=500)
            
            tool_response = {
                "id": "chatcmpl-" + completion.id,
                "object": "chat.completion",
                "created": completion.created,
                "model": completion.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": tool_calls
                        },
                        "logprobs": None,
                        "finish_reason": "tool_calls"
                    }
                ],
                "usage": {
                    "prompt_tokens": completion.usage.prompt_tokens,
                    "completion_tokens": completion.usage.completion_tokens,
                    "total_tokens": completion.usage.total_tokens
                },
                "system_fingerprint": completion.system_fingerprint
            }

            return JSONResponse(content=tool_response, status_code=200)
        else:
            messages = body["messages"]
            if messages[-1]['role'] == "tool":
                messages[-1]['role'] = "user"
                body['messages'][-1]['content'] = get_func_result_guide(body['messages'][-1]['content'])
            model = body["model"]
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            return JSONResponse(content=completion.model_dump(), status_code=200)
    except Exception as e:
        # Print detailed error message
        print(e)
        return JSONResponse(content={"tool_calls": []}, status_code=500)


