from pydantic import BaseModel
from typing import Dict

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