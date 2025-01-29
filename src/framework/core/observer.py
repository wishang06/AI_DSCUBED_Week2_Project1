from abc import ABC, abstractmethod
from typing import Any

class Observer(ABC):
    @abstractmethod
    def update(self, event):
        pass

    @abstractmethod
    def get_input(self, message: Any) -> str:
        pass

class EngineSubject:
    def __init__(self):
        self._observers = []

    def register(self, observer: Observer):
        self._observers.append(observer)

    def notify(self, event: Any):
        for observer in self._observers:
            observer.update(event)

    def get_input(self, event: Any) -> str:
        for observer in self._observers:
            if observer.get_input:
                return observer.get_input(event)
        raise ValueError("No observer can handle input.")

class DummieEngineSubject:
    def __init__(self):
        pass

    def register(self):
        pass

    def notify(self, event: Any):
        pass

    def get_input(self, event: Any):
        return "Dummie Engine Response"
