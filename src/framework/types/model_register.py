from typing import Dict
from .models import Model
from framework.types.clients import ClientType

ModelRegister: Dict[str, Model] = {
    "gpt-4o-mini": Model(
        name="gpt-4o-mini",
        default_provider=ClientType.OPENAI,
        allowed_providers=[ClientType.OPENAI, ClientType.OPENROUTER],
        provider_name_map={
            ClientType.OPENAI: "gpt-4o-mini",
            ClientType.OPENROUTER: "openai/gpt-4o-mini",
        },
    ),
    "gpt-4o": Model(
        name="gpt-4o",
        default_provider=ClientType.OPENAI,
        allowed_providers=[ClientType.OPENAI, ClientType.OPENROUTER],
        provider_name_map={
            ClientType.OPENAI: "gpt-4o",
            ClientType.OPENROUTER: "openai/chatgpt-4o-latest",
        },
    ),
    "o3-mini": Model(
        name="o3-mini",
        default_provider=ClientType.OPENAI,
        allowed_providers=[ClientType.OPENAI],
        provider_name_map={
            ClientType.OPENAI: "o3-mini",
        },
    ),
    "o1-mini": Model(
        name="o1-mini",
        default_provider=ClientType.OPENAI,
        allowed_providers=[ClientType.OPENAI],
        provider_name_map={
            ClientType.OPENAI: "o1-mini",
        },
    ),
    "gemini-2.0-flash": Model(
        name="gemini-2.0-flash",
        default_provider=ClientType.GEMINI_API,
        allowed_providers=[
            ClientType.GEMINI_API,
            ClientType.GEMINI_VERTEX,
        ],
        provider_name_map={
            ClientType.GEMINI_API: "gemini-2.0-flash-exp",
            ClientType.GEMINI_VERTEX: "google/gemini-2.0-flash-001",
        },
    ),
    "gemini-flash-2.0-thinking": Model(
        name="gemini-flash-2.0-thinking",
        default_provider=ClientType.OPENROUTER,
        allowed_providers=[ClientType.GEMINI_API, ClientType.OPENROUTER],
        provider_name_map={
            ClientType.GEMINI_API: "gemini-2.0-flash-thinking-exp-01-21",
            ClientType.OPENROUTER: "google/gemini-2.0-flash-thinking-exp:free",
        },
    ),
    "gemini-pro-2.0": Model(
        name="gemini-pro-2.0",
        default_provider=ClientType.GEMINI_API,
        allowed_providers=[ClientType.GEMINI_API],
        provider_name_map={
            ClientType.GEMINI_API: "gemini-exp-1206",
        },
    ),
    "claude-3.5-sonnet": Model(
        name="claude-3.5-sonnet",
        default_provider=ClientType.OPENROUTER,
        allowed_providers=[ClientType.OPENROUTER],
        provider_name_map={ClientType.OPENROUTER: "anthropic/claude-3.5-sonnet"},
    ),
    "deepseek-v3": Model(
        name="deepseek-v3",
        default_provider=ClientType.OPENROUTER,
        allowed_providers=[ClientType.DEEPSEEK, ClientType.OPENROUTER],
        provider_name_map={
            ClientType.DEEPSEEK: "deepseek-v3",
            ClientType.OPENROUTER: "deepseek/deepseek-chat",
        },
    ),
    "deepseek-r1": Model(
        name="deepseek-r1",
        default_provider=ClientType.OPENROUTER,
        allowed_providers=[ClientType.DEEPSEEK, ClientType.OPENROUTER],
        openrouter_providers=["DeepSeek", "DeepInfra", "Nebius"],
        provider_name_map={
            ClientType.DEEPSEEK: "deepseek-r1",
            ClientType.OPENROUTER: "deepseek/deepseek-r1",
        },
    ),
    "llama-3.1-405b": Model(
        name="llama-3.1-405b",
        default_provider=ClientType.OPENROUTER,
        allowed_providers=[ClientType.OPENROUTER],
        openrouter_providers=["DeepInfra", "Lambda"],
        provider_name_map={ClientType.OPENROUTER: "meta-llama/llama-3.1-405b-instruct"},
    ),
}
