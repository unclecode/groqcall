import concurrent.futures
import uuid
import json
import math
from fastapi.responses import JSONResponse
from prompts import *
from .base_handler import Handler, Context
from .context import Context
from utils import get_tool_call_response, create_logger, describe
from config import PARSE_ERROR_TRIES, EVALUATION_CYCLES_COUNT
from collections import defaultdict

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
            if not context.is_tool_call:
                return await super().handle(context)

            # Step 1: Prepare the conversation history
            messages = self._prepare_conversation_history(context.messages)

            # Step 2: Prepare tool details and detect the mode of operation
            available_tools, system_message, suffix = self._prepare_tool_details(context)

            # Step 3: Prepare the messages for the model
            new_messages = self._prepare_model_messages(messages, available_tools, suffix, context.messages[-1]['content'], system_message)

            # Step 4: Detect the tool calls
            tool_calls_result = await self.process_tool_calls(context, new_messages)
            tool_calls = tool_calls_result["tool_calls"]

            # Step 5: Handle the situation where no tool calls are detected
            if not tool_calls:
                return await self._handle_no_tool_calls(context, tool_calls_result)

            # Step 6: Process built-in tools and resolve the tool calls
            unresolved_tool_calls, resolved_responses = self._process_builtin_tools(context, tool_calls, tool_calls_result["last_completion"].id)

            if not unresolved_tool_calls:
                context.messages.extend(resolved_responses)
                return await super().handle(context)

            # Step 7: Return the unresolved tool calls to the client
            tool_response = get_tool_call_response(tool_calls_result, unresolved_tool_calls, resolved_responses)
            context.response = tool_response
            return JSONResponse(content=context.response, status_code=200)

    def _prepare_conversation_history(self, messages):
        return [
            f"<{m['role'].lower()}>\n{m['content']}\n</{m['role'].lower()}>"
            for m in messages
            if m["role"] != "system"
        ]

    def _prepare_tool_details(self, context):
        tool_choice = context.params.get("tool_choice", "auto")
        forced_mode = type(tool_choice) == dict and tool_choice.get("type", None) == "function"
        available_tools = []

        if forced_mode:
            tool_choice = tool_choice["function"]["name"]
            available_tools = [t["function"] for t in context.tools if t["function"]["name"] == tool_choice]
            system_message = ENFORCED_SYSTAME_MESSAE
            suffix = get_forced_tool_suffix(tool_choice)
        else:
            tool_choice = "auto"
            available_tools = [t["function"] for t in context.tools]
            system_message = SYSTEM_MESSAGE
            suffix = get_suffix()

        # Add one special tool called "fallback", which is always available, its job is to be used when non of other tools are useful for the user input.
        # available_tools.append({
        #     "name": "fallback", 
        #     "description": "Use this tool when none of the other tools are useful for the user input.",
        #     "arguments": {}}
        # )

        return available_tools, system_message, suffix

    def _prepare_model_messages(self, messages, available_tools, suffix, last_message_content, system_message):
        messages_flatten = "\n".join(messages)
        tools_json = json.dumps(available_tools, indent=4)

        return [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": f"# Conversation History:\n{messages_flatten}\n\n# Available Tools: \n{tools_json}\n\n{suffix}\n{last_message_content}",
            },
        ]

    async def _handle_no_tool_calls(self, context, tool_calls_result):
        if context.no_tool_behaviour == "forward":
            context.tools = None
            return await super().handle(context)
        else:
            context.response = {"tool_calls": []}
            tool_response = get_tool_call_response(tool_calls_result, [], [])
            missed_tool_logger.debug(f"Last message content: {context.last_message['content']}")
            return JSONResponse(content=tool_response, status_code=200)

    def _process_builtin_tools(self, context, tool_calls, tool_calls_result_id):
        unresolved_tool_calls = [
            t
            for t in tool_calls
            if t["function"]["name"] not in context.builtin_tool_names
        ]
        resolved_responses = []

        for tool in tool_calls:
            for bt in context.builtin_tools:
                if tool["function"]["name"] == bt["function"]["name"]:
                    res = bt["run"](**{**json.loads(tool["function"]["arguments"]), **bt["extra"]})
                    resolved_responses.append({
                        "name": tool["function"]["name"],
                        "role": "tool",
                        "content": json.dumps(res),
                        "tool_call_id": "chatcmpl-" + tool_calls_result_id,
                    })

        return unresolved_tool_calls, resolved_responses

    async def handle1(self, context: Context):
        body = context.body
        if context.is_tool_call:
            # Step 1: Prepare the the history of conversation.
            messages = [
                f"<{m['role'].lower()}>\n{m['content']}\n</{m['role'].lower()}>"
                for m in context.messages
                if m["role"] != "system"
            ]
            messages_flatten = "\n".join(messages)
            

            # Step 2: Prepare tools details and detect the mode of operation.
            tool_choice = context.params.get("tool_choice", "auto")
            forced_mode = type(tool_choice) == dict and tool_choice.get("type", None) == "function"

            if forced_mode:
                tool_choice = tool_choice["function"]["name"]
                tools_json = json.dumps([t["function"] for t in context.tools if t["function"]["name"] == tool_choice], indent=4)
                system_message = ENFORCED_SYSTAME_MESSAE
                suffix = get_forced_tool_suffix(tool_choice)
            else:
                tool_choice = "auto"
                tools_json = json.dumps([t["function"] for t in context.tools], indent=4)
                system_message = SYSTEM_MESSAGE
                suffix = SUFFIX

            # Step 3: Prepare the messages for the model.
            new_messages = [
                {"role": "system", "content": system_message},
                {
                    "role": "user",
                    "content": f"# Conversation History:\n{messages_flatten}\n\n# Available Tools: \n{tools_json}\n\n{suffix}\n{context.messages[-1]['content']}",
                },
            ]

            # Step 4: Detect the tool calls.
            tool_calls_result = await self.process_tool_calls(context, new_messages)
            tool_calls = tool_calls_result["tool_calls"]

            
            # Step 5: Handle the situation where no tool calls are detected.
            if not tool_calls:
                if context.no_tool_behaviour == "forward":
                    context.tools = None
                    return await super().handle(context)
                else:
                    context.response = {"tool_calls": []}
                    tool_response = get_tool_call_response(tool_calls_result, [], [])
                    missed_tool_logger.debug(
                        f"Last message content: {context.last_message['content']}"
                    )
                    return JSONResponse(content=tool_response, status_code=200)

            
            # Step 6: Process built-in toola and resolve the tool calls, here on the server. In case there is unresolved tool calls, we will return the tool calls to the client to resolve them. But if all tool calls are resolved, we will continue to the next handler.
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
                                "tool_call_id": "chatcmpl-" + tool_calls_result.id,
                            }
                        )

                if not unresolved_tol_calls:
                    context.messages.extend(resolved_responses)
                    return await super().handle(context)

            # Step 7: If reach here, it means there are unresolved tool calls. We will return the tool calls to the client to resolve them.
            tool_response = get_tool_call_response(
                tool_calls_result, unresolved_tol_calls, resolved_responses
            )

            context.response = tool_response
            return JSONResponse(content=context.response, status_code=200)

        return await super().handle(context)

    async def process_tool_calls(self, context, new_messages):
        try:
            evaluation_cycles_count = EVALUATION_CYCLES_COUNT

            def call_route(messages):
                completion = context.client.route(
                    model=context.client.parser_model,
                    messages=messages,
                    temperature=0,
                    max_tokens=512,
                    top_p=1,
                    stream=False,
                )

                response = completion.choices[0].message.content
                response = response.replace("\_", "_")
                if TOOLS_OPEN_TOKEN in response:
                    response = response.split(TOOLS_OPEN_TOKEN)[1].split(
                        TOOLS_CLOSE_TOKEN
                    )[0]
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]

                try:
                    tool_response = json.loads(response)
                    if isinstance(tool_response, list):
                        tool_response = {"tool_calls": tool_response}
                    # Check all detected functions exist in the available tools
                    valid_names = [t['function']["name"] for t in context.tools]
                    available_tools = [t for t in tool_response.get("tool_calls", []) if t['name'] in valid_names]
                    tool_response = {
                        "tool_calls": available_tools,
                    }
                    # tool_response = {"tool_calls": []}
                        
                    
                    return tool_response.get("tool_calls", []), completion
                except json.JSONDecodeError as e:
                    print(f"Error parsing the tool response: {e}")
                    return [], None

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(call_route, new_messages)
                    for _ in range(evaluation_cycles_count)
                ]
                results = [
                    future.result()
                    for future in concurrent.futures.as_completed(futures)
                ]

            tool_calls_list, completions = zip(*results)

            tool_calls_count = defaultdict(int)
            for tool_calls in tool_calls_list:
                for func in tool_calls:
                    tool_calls_count[func["name"]] += 1

            pickup_threshold = max(evaluation_cycles_count, int(evaluation_cycles_count * 0.7))
            final_tool_calls = []
            for tool_calls in tool_calls_list:
                for func in tool_calls:
                    if tool_calls_count[func["name"]] >= pickup_threshold:
                        # ppend if function is not already in the list
                        if not any(
                            f['function']["name"] == func["name"] for f in final_tool_calls
                        ):
                            final_tool_calls.append(
                                {
                                    "id": f"call_{func['name']}_{str(uuid.uuid4())}",
                                    "type": "function",
                                    "function": {
                                        "name": func["name"],
                                        "arguments": json.dumps(func["arguments"]),
                                    },
                                }
                            )

            total_prompt_tokens = sum(c.usage.prompt_tokens for c in completions if c)
            total_completion_tokens = sum(
                c.usage.completion_tokens for c in completions if c
            )
            total_tokens = sum(c.usage.total_tokens for c in completions if c)

            last_completion = completions[-1] if completions else None

            return {
                "tool_calls": final_tool_calls,
                "last_completion": last_completion,
                "usage": {
                    "prompt_tokens": total_prompt_tokens,
                    "completion_tokens": total_completion_tokens,
                    "total_tokens": total_tokens,
                },
            }

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

            try:
                params = {
                    "temperature": 0.5,
                    "max_tokens": 1024,
                }
                params = {**params, **context.params}

                completion = context.client.route(
                    messages=messages,
                    **context.client.clean_params(params),
                )
                context.response = completion.model_dump()
                return JSONResponse(content=context.response, status_code=200)
            except Exception as e:
                raise e

        return await super().handle(context)
