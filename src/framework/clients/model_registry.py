from typing import Dict, Optional, List

from framework.types.models import Model
from framework.types.clients import ClientType
from framework.types.model_register import ModelRegister


class ModelRegistry:
    """Central registry of all available models and their configurations"""

    def __init__(self):
        self._models = ModelRegister

    def get_model(self, model_name: str) -> Model:
        """Get information about a specific model"""
        if model_name not in self._models:
            raise ValueError(f"Unknown model: {model_name}")
        return self._models[model_name]

    def get_provider_model_name(self, model_info: Model, provider: ClientType) -> str:
        """Get the provider-specific model name"""
        # Simply use the provider_model_names mapping
        return model_info.provider_name_map.get(provider)

    def list_models(self, provider: Optional[ClientType] = None) -> List[str]:
        """List all available models, optionally filtered by provider"""
        if provider:
            return [
                name
                for name, info in self._models.items()
                if provider in info.allowed_providers
            ]
        return list(self._models.keys())
