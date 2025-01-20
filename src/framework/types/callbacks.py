
from abc import ABC, abstractmethod

class StatusCallback(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> None:
        """Basic message execution"""
        pass
    
    @abstractmethod
    def __enter__(self):
        """Enter loading state"""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, 
                 exc_val,
                 exc_tb) -> None:
        """Exit loading state"""
        pass
    
    @abstractmethod
    def update_status(self, message: str) -> None:
        """Update loading state message"""
        pass

    @abstractmethod
    def get_input(self, message: str) -> str:
        """Get input from user"""
        pass

class SimpleCallback(ABC):
    """
    Simply sends a message to the stack above
    """
    @abstractmethod
    def do(self, **kwargs):
        pass
