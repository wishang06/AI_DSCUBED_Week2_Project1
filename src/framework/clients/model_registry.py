from typing import Dict, Optional, List

from src.framework.types.models import ModelInfo
from src.framework.types.clients import ClientType

class ModelRegistry:
    """Central registry of all available models and their configurations"""

    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._initialize_models()

    def _initialize_models(self):
        """Initialize the model registry with known models"""
        # GPT-4 Models
        self._models["gpt-4o-mini"] = ModelInfo(
            name="gpt-4o-mini",
            default_provider=ClientType.OPENAI,
            allowed_providers=[ClientType.OPENAI, ClientType.OPENROUTER],
            provider_name_map={
                ClientType.OPENAI: "gpt-4o-mini",
                ClientType.OPENROUTER: "openai/gpt-4o-mini",
            }
        )
        self._models["gpt-4o"] = ModelInfo(
            name="gpt-4o",
            default_provider=ClientType.OPENAI,
            allowed_providers=[ClientType.OPENAI, ClientType.OPENROUTER],
            provider_name_map={
                ClientType.OPENAI: "gpt-4o",
                ClientType.OPENROUTER: "openai/chatgpt-4o-latest",
            }
        )
        self._models["gemini-flash-2.0"] = ModelInfo(
            name="gemini-flash-2.0",
            default_provider=ClientType.GEMINI_API,
            allowed_providers=[ClientType.GEMINI_API],
            provider_name_map={
                ClientType.GEMINI_API: "gemini-2.0-flash-exp",
            }
        )
        self._models["gemini-flash-2.0-thinking"] = ModelInfo(
            name="gemini-flash-2.0-thinking",
            default_provider=ClientType.OPENROUTER,
            allowed_providers=[ClientType.GEMINI_API, ClientType.OPENROUTER],
            provider_name_map={
                ClientType.GEMINI_API: "gemini-2.0-flash-thinking-exp-01-21",
                ClientType.OPENROUTER: "google/gemini-2.0-flash-thinking-exp:free",
            }
        )
        self._models["gemini-pro-2.0"] = ModelInfo(
            name="gemini-pro-2.0",
            default_provider=ClientType.GEMINI_API,
            allowed_providers=[ClientType.GEMINI_API],
            provider_name_map={
                ClientType.GEMINI_API: "gemini-exp-1206",
            }
        )
        self._models["claude-3.5-sonnet"] = ModelInfo(
            name="claude-3.5-sonnet",
            default_provider=ClientType.OPENROUTER,
            allowed_providers=[ClientType.OPENROUTER],
            provider_name_map={
                ClientType.OPENROUTER: "anthropic/claude-3.5-sonnet"
            }
        )
        self._models["deepseek-v3"] = ModelInfo(
            name="deepseek-v3",
            default_provider=ClientType.OPENROUTER,
            allowed_providers=[ClientType.DEEPSEEK, ClientType.OPENROUTER],
            provider_name_map={
                ClientType.DEEPSEEK: "deepseek-v3",
                ClientType.OPENROUTER: "deepseek/deepseek-chat",
            }
        )
        self._models["deepseek-r1"] = ModelInfo(
            name="deepseek-r1",
            default_provider=ClientType.DEEPSEEK,
            allowed_providers=[ClientType.DEEPSEEK, ClientType.OPENROUTER],
            openrouter_providers=["DeepSeek", "DeepInfra"],
            provider_name_map={
                ClientType.DEEPSEEK: "deepseek-r1",
                ClientType.OPENROUTER: "deepseek/deepseek-r1",
            }
        )
        self._models["llama-3.1-405b"] = ModelInfo(
            name="llama-3.1-405b",
            default_provider=ClientType.OPENROUTER,
            allowed_providers=[ClientType.OPENROUTER],
            openrouter_providers=["DeepInfra", "Lambda"],
            provider_name_map={
                ClientType.OPENROUTER: "meta-llama/llama-3.1-405b-instruct"
            }
        )


    def get_model_info(self, model_name: str) -> ModelInfo:
        """Get information about a specific model"""
        if model_name not in self._models:
            raise ValueError(f"Unknown model: {model_name}")
        return self._models[model_name]

    def get_provider_model_name(self, model_info: ModelInfo, provider: ClientType) -> str:
        """Get the provider-specific model name"""
        # Simply use the provider_model_names mapping
        return model_info.provider_name_map.get(provider)

    def list_models(self, provider: Optional[ClientType] = None) -> List[str]:
        """List all available models, optionally filtered by provider"""
        if provider:
            return [name for name, info in self._models.items()
                    if provider in info.allowed_providers]
        return list(self._models.keys())
