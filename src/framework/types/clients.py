from enum import Enum, auto
from typing import Dict

class ClientType(Enum):
    OPENAI = auto()
    GEMINI_VERTEX = auto()
    GEMINI_API = auto()
    OPENROUTER = auto()
    DEEPSEEK = auto()
    ANTHROPIC = auto()

ClientKeyMap: Dict[ClientType, str] = {
    ClientType.OPENAI: "OPENAI_API_KEY",
    ClientType.GEMINI_API: "GEMINI_API_KEY",
    ClientType.OPENROUTER: "OPENROUTER_API_KEY",
    ClientType.DEEPSEEK: "DEEPSEEK_API_KEY",
    ClientType.ANTHROPIC: "ANTHROPIC_API_KEY",
}

class OpenAIReasoningAPIFormat(Enum):
    OPENROUTER = auto()
    DEEPSEEK = auto()
    GEMINI = auto()
