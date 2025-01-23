from abc import ABC, abstractmethod
from typing import Any

class Interface(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def get(self, request: Any) -> str:
        pass

    @abstractmethod
    def out(self, content: Any) -> str:
        pass

class DummyInterface(Interface):
    def __init__(self, **kwargs):
        pass

    def get(self, request: Any) -> str:
        return "DummyInterface get"

    def out(self, content: Any) -> str:
        return "DummyInterface out"
