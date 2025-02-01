from typing import List, Optional, Union
import os

from src.framework.clients.model_registry import ModelRegistry
from src.framework.clients.openai_client import ClientOpenAI
from src.framework.clients.openrouter_client import ClientOpenRouter
from src.framework.types.models import ClientSetupConfig, ModelRequestConfig
from src.framework.utils.runtime import get_global_runtime
from src.framework.types.openrouter_providers import OpenRouterProvider
from src.framework.types.clients import ClientType, ClientKeyMap


class ClientManager:
    """Manages client instances and model configurations"""

    def __init__(self):
        self.registry = ModelRegistry()
        self.runtime = get_global_runtime()
        if not self.runtime:
            raise RuntimeError("Global runtime not initialized")

        self._initialize_client_factories()

    def _initialize_client_factories(self):
        """Initialize factory methods for different client types"""
        self._client_factories = {
            ClientType.OPENAI: self._create_openai_client,
            ClientType.OPENROUTER: self._create_openrouter_client,
            ClientType.GEMINI_API: self._create_gemini_api_client,
            ClientType.GEMINI_VERTEX: self._create_gemini_vertex_client,
            ClientType.DEEPSEEK: self._create_deepseek_client,
        }

    def _create_openai_client(self, config: ClientSetupConfig) -> ClientOpenAI:
        """Create an OpenAI client"""
        return ClientOpenAI.create_openai(config.api_key)

    def _create_openrouter_client(self, config: ClientSetupConfig) -> ClientOpenRouter:
        """Create an OpenRouter client"""
        return ClientOpenRouter(config.api_key)

    def _create_gemini_vertex_client(self, config: ClientSetupConfig) -> ClientOpenAI:
        """Create a Google client"""
        if not config.project_id or not config.location:
            raise ValueError("project_id and location required for Google client")
        return ClientOpenAI.create_gemini_vertex(config.project_id, config.location)

    def _create_gemini_api_client(self, config: ClientSetupConfig) -> ClientOpenAI:
        """Create a Gemini API client"""
        return ClientOpenAI.create_gemini(config.api_key)

    def _create_deepseek_client(self, config: ClientSetupConfig) -> ClientOpenAI:
        """Create a DeepSeek client"""
        return ClientOpenAI.create_deepseek(config.api_key)

    def get_or_create_client(self, config: ClientSetupConfig) -> Union[ClientOpenAI, ClientOpenRouter]:
        """Get an existing client or create a new one"""
        # Check if client already exists in runtime
        if self.runtime.client_list:
            for client in self.runtime.client_list:
                if client.type == config.provider:
                    return client

        # Create new client
        factory = self._client_factories.get(config.provider)
        if not factory:
            raise ValueError(f"Unsupported provider: {config.provider}")

        # noinspection PyArgumentList
        client = factory(config)

        self.runtime.client_list.append(client)
        return client

    def get_client_for_model(self, model_request: ModelRequestConfig) -> Union[ClientOpenAI, ClientOpenRouter]:
        """Get appropriate client for a model configuration"""
        model_info = self.registry.get_model_info(model_request.model_name)

        client_config = ClientSetupConfig(
            provider=model_request.provider,
            api_key=os.getenv(f"{ClientKeyMap[model_request.provider]}")
        )

        if model_request.provider == ClientType.GEMINI_VERTEX:
            client_config.project_id = os.getenv("GOOGLE_PROJECT_ID")
            client_config.location = os.getenv("GOOGLE_LOCATION")

        return self.get_or_create_client(client_config)


def set_model(model_name: str,
              provider: Optional[ClientType] = None,
              openrouter_providers: Optional[List[OpenRouterProvider]] = None) -> tuple[
    Union[ClientOpenAI, ClientOpenRouter], str]:
    """
    High-level function to set up a model with specified provider

    Args:
        model_name: Name of the model to use
        provider: Optional provider override (uses default if not specified)
        openrouter_providers: Optional specific provider for OpenRouter models

    Returns:
        tuple: (client instance, actual model name to use)
    """
    manager = ClientManager()
    model_info = manager.registry.get_model_info(model_name)

    if not provider:
        provider = model_info.default_provider

    model_config = ModelRequestConfig(
        model_name=model_name,
        provider=provider,
        openrouter_providers=openrouter_providers
    )

    client = manager.get_client_for_model(model_config)
    if client.type == ClientType.OPENROUTER:
        if not openrouter_providers:
            if model_info.openrouter_providers:
                client.set_model_providers(model_name, model_info.openrouter_providers)
        else:
            client.set_model_providers(model_name, openrouter_providers)

    # Get the appropriate model name for the chosen provider
    actual_model_name = manager.registry.get_provider_model_name(
        model_info, provider)

    return client, actual_model_name
