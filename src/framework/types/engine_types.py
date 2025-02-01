from pydantic import BaseModel
from typing import Literal, TypeAlias, Dict, Union, Type
from enum import Enum, auto
from src.framework.core.engine import ToolEngine, SimpleChatEngine

class EngineType(str, Enum):
    ToolEngine = auto()
    SimpleChatEngine = auto()

EngineTypeMap: Dict[EngineType | str, Type[ToolEngine | SimpleChatEngine] | EngineType] = {
    "ToolEngine": EngineType.ToolEngine,
    EngineType.ToolEngine: ToolEngine,
    "SimpleChatEngine": EngineType.SimpleChatEngine,
    EngineType.SimpleChatEngine: SimpleChatEngine}
