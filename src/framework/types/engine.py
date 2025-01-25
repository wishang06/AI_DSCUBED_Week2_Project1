from abc import ABC, abstractmethod

class Engine(ABC):
    @abstractmethod
    def execute(self, prompt: str):
        pass
