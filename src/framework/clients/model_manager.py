from typing import Union
import os

from framework.clients.model_registry import ModelRegistry
from framework.clients.openai_client import ClientOpenAI
from framework.clients.openrouter_client import ClientOpenRouter
from framework.types.clients import ClientType, ClientKeyMap
from framework.utils.singleton import singleton
from framework.types.models import (
    ModelInstanceRequest,
    ClientSetupConfig,
    ModelInstance,
    Model,
)

from dotenv import load_dotenv

load_dotenv(".env")


@singleton
class ModelManager:
    """Manages client instances and model configurations"""

    def __init__(self):
        self.active_clients = []
        self.registry = ModelRegistry()
        self._initialize_client_factories()

    def _initialize_client_factories(self):
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
        return ClientOpenAI.create_openrouter(config.api_key)

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

    def get_or_create_client(
        self, config: ClientSetupConfig
    ) -> Union[ClientOpenAI, ClientOpenRouter]:
        """Get an existing client or create a new one"""
        # Check if client already exists in runtime
        if self.active_clients:
            for client in self.active_clients:
                if client.type == config.client:
                    return client

        # Create new client
        factory = self._client_factories.get(config.client)
        if not factory:
            raise ValueError(f"Unsupported provider: {config.client}")

        # noinspection PyArgumentList
        client = factory(config)

        self.active_clients.append(client)
        return client

    def get_client_for_model(
        self, client_type: ClientType
    ) -> Union[ClientOpenAI, ClientOpenRouter]:
        if client_type == ClientType.GEMINI_VERTEX:
            client_config = ClientSetupConfig(
                client=client_type,
                project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=os.getenv("GOOGLE_CLOUD_LOCATION"),
            )
        else:
            client_config = ClientSetupConfig(
                client=client_type,
                api_key=os.getenv(f"{ClientKeyMap[client_type]}"),
            )

        return self.get_or_create_client(client_config)

    def get_model_instance(self, model_request: ModelInstanceRequest) -> ModelInstance:
        """Create a ModelInstance based on the provided request.

        Args:
            model_request: Configuration for the requested model instance

        Returns:
            ModelInstance configured according to the request and defaults
        """
        # Get base model info
        model = self.registry.get_model(model_request.model_name)

        # Determine provider
        provider = self._get_provider(model_request, model)

        # Get provider-specific model name
        provider_model_name = self.registry.get_provider_model_name(
            model, provider.type
        )

        # Handle OpenRouter specific configuration
        openrouter_providers = None
        if provider.type == ClientType.OPENROUTER:
            openrouter_providers = (
                model_request.openrouter_provider or model.openrouter_providers
            )
        return ModelInstance(
            model=model,
            provider=provider,
            provider_model_name=provider_model_name,
            openrouter_provider=openrouter_providers,
            model_extras=model_request.model_extras,
        )

    def _get_provider(
        self, model_request: ModelInstanceRequest, model: Model
    ) -> Union[ClientOpenAI, ClientOpenRouter]:
        """Determine the appropriate provider based on request and model defaults."""
        provider_type = model_request.provider or model.default_provider
        return self.get_client_for_model(provider_type)
