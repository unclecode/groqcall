from abc import ABC, abstractmethod
from typing import Any, Dict
from importlib import import_module
import json
import uuid
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from providers import BaseProvider
from prompts import *
from providers import GroqProvider
import importlib
from utils import get_tool_call_response, create_logger, describe

missed_tool_logger = create_logger(
    "chain.missed_tools", ".logs/empty_tool_tool_response.log"
)


class Context:
    def __init__(self, request: Request, provider: str, body: Dict[str, Any]):
        self.request = request
        self.provider = provider
        self.body = body
        self.response = None

        # extract all keys from body except messages and tools and set in params
        self.params = {k: v for k, v in body.items() if k not in ["messages", "tools"]}

        # self.no_tool_behaviour = self.params.get("no_tool_behaviour", "return")
        self.no_tool_behaviour = self.params.get("no_tool_behaviour", "forward")
        self.params.pop("no_tool_behaviour", None)

        # Todo: For now, no stream, sorry ;)
        self.params["stream"] = False

        self.messages = body.get("messages", [])
        self.tools = body.get("tools", [])

        self.builtin_tools = [
            t for t in self.tools if "parameters" not in t["function"]
        ]
        self.builtin_tool_names = [t["function"]["name"] for t in self.builtin_tools]
        self.custom_tools = [t for t in self.tools if "parameters" in t["function"]]

        for bt in self.builtin_tools:
            func_namespace = bt["function"]["name"]
            if len(func_namespace.split(".")) == 2:
                module_name, func_class_name = func_namespace.split(".")
                func_class_name = f"{func_class_name.capitalize()}Function"
                # raise ValueError("Only one builtin function can be called at a time.")
                module = importlib.import_module(f"app.functions.{module_name}")
                func_class = getattr(module, func_class_name, None)
                schema_dict = func_class.get_schema()
                if schema_dict:
                    bt["function"] = schema_dict
                    bt["run"] = func_class.run
                    bt["extra"] = self.params.get("extra", {})
                    self.params.pop("extra", None)

        self.client: BaseProvider = None

    @property
    def last_message(self):
        return self.messages[-1] if self.messages else {}

    @property
    def is_tool_call(self):
        return bool(
            self.last_message["role"] == "user"
            and self.tools
            and self.params.get("tool_choice", "none") != "none"
        )

    @property
    def is_tool_response(self):
        return bool(self.last_message["role"] == "tool" and self.tools)

    @property
    def is_normal_chat(self):
        return bool(not self.is_tool_call and not self.is_tool_response)


class Handler(ABC):
    """Abstract Handler class for building the chain of handlers."""

    _next_handler: "Handler" = None

    def set_next(self, handler: "Handler") -> "Handler":
        self._next_handler = handler
        return handler

    @abstractmethod
    async def handle(self, context: Context):
        if self._next_handler:
            try:
                return await self._next_handler.handle(context)
            except Exception as e:
                _exception_handler: "Handler" = ExceptionHandler()
                # Extract the stack trace and log the exception
                return await _exception_handler.handle(context, e)


class ProviderSelectionHandler(Handler):
    @staticmethod
    def provider_exists(provider: str) -> bool:
        module_name = f"app.providers"
        class_name = f"{provider.capitalize()}Provider"
        try:
            provider_module = import_module(module_name)
            provider_class = getattr(provider_module, class_name)
            return bool(provider_class)
        except ImportError:
            return False

    async def handle(self, context: Context):
        # Construct the module path and class name based on the provider
        module_name = f"app.providers"
        class_name = f"{context.provider.capitalize()}Provider"

        try:
            # Dynamically import the module and class
            provider_module = import_module(module_name)
            provider_class = getattr(provider_module, class_name)

            if provider_class:
                context.client = provider_class(
                    api_key=context.api_token
                )  # Assuming an api_key parameter
                return await super().handle(context)
            else:
                raise ValueError(
                    f"Provider class {class_name} could not be found in {module_name}."
                )
        except ImportError as e:
            # Handle import error (e.g., module or class not found)
            print(f"Error importing {class_name} from {module_name}: {e}")
            context.response = {
                "error": f"An error occurred while trying to load the provider: {e}"
            }
            return JSONResponse(content=context.response, status_code=500)


class ImageMessageHandler(Handler):
    async def handle(self, context: Context):
        new_messages = []
        image_ref = 1
        for message in context.messages:
            if message["role"] == "user":
                if isinstance(message["content"], list):
                    prompt = None
                    for content in message["content"]:
                        if content["type"] == "text":
                            # new_messages.append({"role": message["role"], "content": content["text"]})
                            prompt = content["text"]
                        elif content["type"] == "image_url":
                            image_url = content["image_url"]["url"]
                            try:
                                prompt = prompt or IMAGE_DESCRIPTO_PROMPT
                                description = describe(prompt, image_url)
                                if description:
                                    description = get_image_desc_guide(image_ref, description)
                                    new_messages.append(
                                        {"role": message["role"], "content": description}
                                    )
                                    image_ref += 1
                                else:
                                    pass
                            except Exception as e:
                                print(f"Error describing image: {e}")
                                continue
                else:
                    new_messages.append(message)
            else:
                new_messages.append(message)

        context.messages = new_messages
        return await super().handle(context)
    

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
                f"{m['role'].title()}: {m['content']}"
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

            new_messages = [
                {"role": "system", "content": system_message},
                {
                    "role": "system",
                    "content": f"Conversation History:\n{''.join(messages)}\n\nTools: \n{tools_json}\n\n{suffix}",
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


class DefaultCompletionHandler(Handler):
    async def handle(self, context: Context):
        if context.is_normal_chat:
            # Assuming context.client is set and has a method for creating chat completions
            completion = context.client.route(
                messages=context.messages,
                **context.client.clean_params(context.params),
            )
            context.response = completion.model_dump()
            return JSONResponse(content=context.response, status_code=200)

        return await super().handle(context)


class FallbackHandler(Handler):
    async def handle(self, context: Context):
        # This handler does not pass the request further down the chain.
        # It acts as a fallback when no other handler has processed the request.
        if not context.response:
            # The default action when no other handlers have processed the request
            context.response = {"message": "No suitable action found for the request."}
            return JSONResponse(content=context.response, status_code=400)

        # If there's already a response set in the context, it means one of the handlers has processed the request.
        return JSONResponse(content=context.response, status_code=200)


class ExceptionHandler(Handler):
    async def handle(self, context: Context, exception: Exception):
        print(f"Error processing the request: {exception}")
        print(traceback.format_exc())
        return JSONResponse(
            content={"error": "An unexpected error occurred. " + str(exception)},
            status_code=500,
        )
