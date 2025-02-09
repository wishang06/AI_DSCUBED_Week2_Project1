from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LLMClient(ABC):
    @abstractmethod
    def create_completion(
        self, model: , **kwargs
    ):
        pass

    @abstractmethod
    def create_streaming_completion(
        self, model_name: str, context: List[Dict[str, Any]], **kwargs
    ):
        pass
