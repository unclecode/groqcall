import json
import uuid
from fastapi.responses import JSONResponse
from prompts import *
from utils import get_tool_call_response, describe
from .base_handler import Handler, Context
from .context import Context
from utils import get_tool_call_response, create_logger, describe

missed_tool_logger = create_logger(
    "chain.missed_tools", ".logs/empty_tool_tool_response.log"
)


class ImageLLavaMessageHandler(Handler):
    async def handle(self, context: Context):
        new_messages = []
        image_ref = 1
        for message in context.messages:
            new_messages.append(message)
            if message["role"] == "user":
                if isinstance(message["content"], list):
                    for content in message["content"]:
                        if content["type"] == "text":
                            prompt = content["text"]
                        elif content["type"] == "image_url":
                            image_url = content["image_url"]["url"]
                            try:
                                description = describe(prompt, image_url)
                                new_messages.append(
                                    {"role": "assistant", "content": description}
                                )
                                image_ref += 1
                            except Exception as e:
                                print(f"Error describing image: {e}")
                                continue
        context.messages = new_messages
        return await super().handle(context)


class ToolExtractionHandler(Handler):
    async def handle(self, context: Context):
        body = context.body
        if context.is_tool_call:
            # Prepare the messages and tools for the tool extraction
            messages = [
                f"<{m['role'].lower()}>\n{m['content']}\n</{m['role'].lower()}>"
                for m in context.messages
                if m["role"] != "system"
            ]
            tools_json = json.dumps([t["function"] for t in context.tools], indent=4)

            # Process the tool_choice
            tool_choice = context.params.get("tool_choice", "auto")
            forced_mode = False
            if (
                type(tool_choice) == dict
                and tool_choice.get("type", None) == "function"
            ):
                tool_choice = tool_choice["function"].get("name", None)
                if not tool_choice:
                    raise ValueError(
                        "Invalid tool choice. 'tool_choice' is set to a dictionary with 'type' as 'function', but 'function' does not have a 'name' key."
                    )
                forced_mode = True

                # Regenerate the string tool_json and keep only the forced tool
                tools_json = json.dumps(
                    [
                        t["function"]
                        for t in context.tools
                        if t["function"]["name"] == tool_choice
                    ],
                    indent=4,
                )

            system_message = (
                SYSTEM_MESSAGE if not forced_mode else ENFORCED_SYSTAME_MESSAE
            )
            suffix = SUFFIX if not forced_mode else get_forced_tool_suffix(tool_choice)

            messages_flatten = '\n'.join(messages)

            new_messages = [
                {"role": "system", "content": system_message},
                {
                    "role": "system",
                    "content": f"# Conversation History:\n{messages_flatten}\n\n# Available Tools: \n{tools_json}\n\n{suffix}",
                },
            ]

            completion, tool_calls = await self.process_tool_calls(
                context, new_messages
            )

            if not tool_calls:
                if context.no_tool_behaviour == "forward":
                    context.tools = None
                    return await super().handle(context)
                else:
                    context.response = {"tool_calls": []}
                    tool_response = get_tool_call_response(completion, [], [])
                    missed_tool_logger.debug(
                        f"Last message content: {context.last_message['content']}"
                    )
                    return JSONResponse(content=tool_response, status_code=200)

            unresolved_tol_calls = [
                t
                for t in tool_calls
                if t["function"]["name"] not in context.builtin_tool_names
            ]
            resolved_responses = []
            for tool in tool_calls:
                for bt in context.builtin_tools:
                    if tool["function"]["name"] == bt["function"]["name"]:
                        res = bt["run"](
                            **{
                                **json.loads(tool["function"]["arguments"]),
                                **bt["extra"],
                            }
                        )
                        resolved_responses.append(
                            {
                                "name": tool["function"]["name"],
                                "role": "tool",
                                "content": json.dumps(res),
                                "tool_call_id": "chatcmpl-" + completion.id,
                            }
                        )

                if not unresolved_tol_calls:
                    context.messages.extend(resolved_responses)
                    return await super().handle(context)

            tool_response = get_tool_call_response(
                completion, unresolved_tol_calls, resolved_responses
            )

            context.response = tool_response
            return JSONResponse(content=context.response, status_code=200)

        return await super().handle(context)

    async def process_tool_calls(self, context, new_messages):
        try:
            tries = 5
            tool_calls = []
            while tries > 0:
                try:
                    # Assuming the context has an instantiated client according to the selected provider
                    completion = context.client.route(
                        model=context.client.parser_model,
                        messages=new_messages,
                        temperature=0,
                        max_tokens=1024,
                        top_p=1,
                        stream=False,
                    )

                    response = completion.choices[0].message.content
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0]

                    try:
                        tool_response = json.loads(response)
                        if isinstance(tool_response, list):
                            tool_response = {"tool_calls": tool_response}
                    except json.JSONDecodeError as e:
                        print(
                            f"Error parsing the tool response: {e}, tries left: {tries}"
                        )
                        new_messages.append(
                            {
                                "role": "user",
                                "content": f"Error: {e}.\n\n{CLEAN_UP_MESSAGE}",
                            }
                        )
                        tries -= 1
                        continue

                    for func in tool_response.get("tool_calls", []):
                        tool_calls.append(
                            {
                                "id": f"call_{func['name']}_{str(uuid.uuid4())}",
                                "type": "function",
                                "function": {
                                    "name": func["name"],
                                    "arguments": json.dumps(func["arguments"]),
                                },
                            }
                        )

                    break
                except Exception as e:
                    raise e

            if tries == 0:
                tool_calls = []

            return completion, tool_calls
        except Exception as e:
            print(f"Error processing the tool calls: {e}")
            raise e


class ToolResponseHandler(Handler):
    async def handle(self, context: Context):
        body = context.body
        if context.is_tool_response:
            messages = context.messages

            for message in messages:
                if message["role"] == "tool":
                    message["role"] = "user"
                    message["content"] = get_func_result_guide(message["content"])

            messages[-1]["role"] = "user"
            # Assuming get_func_result_guide is a function that formats the tool response
            messages[-1]["content"] = get_func_result_guide(messages[-1]["content"])

            try:
                completion = context.client.route(
                    messages=messages,
                    **context.client.clean_params(context.params),
                )
                context.response = completion.model_dump()
                return JSONResponse(content=context.response, status_code=200)
            except Exception as e:
                # Log the exception or handle it as needed
                print(e)
                context.response = {
                    "error": "An error occurred processing the tool response"
                }
                return JSONResponse(content=context.response, status_code=500)

        return await super().handle(context)
