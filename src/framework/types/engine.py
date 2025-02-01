from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

class ToolEngineMode(Enum):
    NORMAL = auto()
    MINIMAL = auto()
    CHAIN = auto()
    LINEAR_CHAIN = auto()

class Engine(ABC):
    @abstractmethod
    def subscribe(self, observer):
        pass

    @abstractmethod
    def execute(self, prompt: str):
        pass
