import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, NewType, Union

# TODO use _type


# Type for tool function
ToolFunction = Callable[..., Any]
AsyncToolFunction = Callable[..., "asyncio.Future[Any]"]
AsyncOrSyncToolFunction = Union[ToolFunction, AsyncToolFunction]


ModelFormattedDictTool = NewType("ModelFormattedDictTool", dict[str, Any])
ContextType = NewType("ContextType", List[Dict[str, Any]])

ModelNameStr = NewType("ModelNameStr", str)


# TODO this is a class not really a type probably put into seperate file


@dataclass
class ToolCall:
    """Represents a tool call from an LLM."""

    id: str
    type: str = "function"
    name: str = ""
    arguments: str = "{}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool call to dictionary format."""
        return {
            "id": self.id,
            "type": self.type,
            "function": {"name": self.name, "arguments": self.arguments},
        }
