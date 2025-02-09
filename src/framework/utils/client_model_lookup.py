from dataclasses import dataclass
from enum import Enum, auto
from framework.clients.openai_client import ClientOpenAI
from framework.clients.openrouter_client import ClientOpenRouter


class Clients(Enum):
    OPENROUTER_CLIENT = auto()
    OPENAI_CLIENT = auto()
    GEMINI_CLIENT = auto()
    DEEPSEEK_CLIENT = auto()
