from typing import Any, Dict
from fastapi import Request
from providers import BaseProvider
from prompts import *
import importlib
from utils import create_logger


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
            and self.params.get("tool_choice", None) != "none"
        )

    @property
    def is_tool_response(self):
        return bool(self.last_message["role"] == "tool" and self.tools)

    @property
    def is_normal_chat(self):
        return bool(not self.is_tool_call and not self.is_tool_response)
