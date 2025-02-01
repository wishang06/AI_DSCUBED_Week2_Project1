from dataclasses import dataclass
from typing import Dict, Optional, List

from src.framework.types.clients import ClientType
from src.framework.types.openrouter_providers import OpenRouterProvider


@dataclass
class ModelInfo:
    """Information about a specific model"""
    name: str  # Our internal reference name
    default_provider: ClientType
    provider_name_map: Dict[ClientType, str]  # Mapping of provider names to model names
    allowed_providers: Optional[List[ClientType]] = None
    openrouter_providers: Optional[List[OpenRouterProvider]] = None


@dataclass
class ClientSetupConfig:
    """Configuration for client initialization"""
    provider: ClientType
    api_key: str
    project_id: Optional[str] = None  # For Google
    location: Optional[str] = None  # For Google


@dataclass
class ModelRequestConfig:
    """Request for a specific model"""
    model_name: str
    provider: Optional[ClientType] = None
    openrouter_providers: Optional[List[OpenRouterProvider]] = None
