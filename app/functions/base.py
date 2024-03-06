from pydantic import BaseModel
from typing import Dict

class Function:
    class Schema(BaseModel):
        pass

    @classmethod
    def get_schema(cls) -> Dict:
        return cls.Schema.schema()