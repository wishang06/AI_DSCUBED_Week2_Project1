from abc import ABC, abstractmethod
from typing import Any

class Observer(ABC):
    @abstractmethod
    def update(self, event):
        pass

    @abstractmethod
    def get_input(self, message: str) -> str:
        pass

class EngineSubject:
    def __init__(self):
        self._observers = []

    def register(self, observer: Observer):
        self._observers.append(observer)

    def notify(self, event: Any):
        for observer in self._observers:
            observer.update(event)

    def get_input(self, message: str) -> str:
        for observer in self._observers:
            if observer.get_input:
                return observer.get_input(message)
        raise ValueError("No observer can handle input.")
