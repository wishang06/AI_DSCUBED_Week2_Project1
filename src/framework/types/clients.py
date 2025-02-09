from enum import Enum, auto
from typing import Dict


class ClientType(Enum):
    OPENAI = "openai"
    GEMINI_VERTEX = "gemini_vertex"
    GEMINI_API = "gemini_api"
    OPENROUTER = "openrouter"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"


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
