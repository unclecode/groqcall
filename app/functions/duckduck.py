from pydantic import BaseModel, Field
from typing import Optional, Dict
import requests
import json
from duckduckgo_search import DDGS

# from .base import Function
from pydantic import Field
from typing import Optional
import requests
import json


class Function:
    name: str
    description: str

    class Schema(BaseModel):
        pass

    @classmethod
    def get_schema(cls) -> Dict:
        schema_dict = {
            "name": cls.name,
            "description": cls.description,
            "parameters": cls.Schema.schema(),
        }
        return schema_dict

class SearchFunction(Function):
    name = "duckduck.search"
    description = "Use this function to search DuckDuckGo for a query.\n\nArgs:\n    query(str): The query to search for.\n    max_results (optional, default=5): The maximum number of results to return.\n\nReturns:\n    The result from DuckDuckGo."

    class Schema(Function.Schema):
        query: str = Field(..., description="The query to search for.")
        max_results: Optional[int] = Field(5, description="The maximum number of results to return.")

    @classmethod
    def run(cls, **kwargs):
        query = kwargs.get("query")
        max_results = kwargs.get("max_results")
        with DDGS() as ddgs:
            return [r for r in ddgs.text(query, safesearch='off', max_results=max_results)]
        

class NewsFunction(Function):
    name = "duckduck.news"
    description = "Use this function to get the latest news from DuckDuckGo.\n\nArgs:\n    query(str): The query to search for.\n    max_results (optional, default=5): The maximum number of results to return.\n\nReturns:\n    The latest news from DuckDuckGo."

    class Schema(Function.Schema):
        query: str = Field(..., description="The query to search for.")
        max_results: Optional[int] = Field(5, description="The maximum number of results to return.")

    @classmethod
    def run(cls, **kwargs):
        query = kwargs.get("query")
        max_results = kwargs.get("max_results")

        with DDGS() as ddgs:
            results = [r for r in ddgs.news(query, safesearch='off', max_results=max_results)]
        return results