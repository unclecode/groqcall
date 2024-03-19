from abc import ABC, abstractmethod
from typing import Dict

class ReasoningBase(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, context) -> Dict:
        pass

