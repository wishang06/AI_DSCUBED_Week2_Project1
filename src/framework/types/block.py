from abc import ABC, abstractmethod


class Block:
    @abstractmethod

    def execute(self, **kwargs) -> None:
        """Basic message execution"""
        pass
