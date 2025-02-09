from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, List, Literal, Union, Any

from framework.types.clients import ClientType
from framework.types.openrouter_providers import OpenRouterProvider
from pydantic import BaseModel, field_validator

__all__ = [
    "ToolChoiceFunction",
    "ToolChoice",
    "ToolConfig",
    "ConfigDefaults",
    "Model",
    "ClientSetupConfig",
    "ModelInstanceRequest",
    "ModelInstance",
    "OpenAIReasoningEffort",
]


class OpenAIReasoningEffort(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolChoiceFunction(BaseModel):
    """
    Attributes:
        name: str
    """

    name: str


class ToolChoice(BaseModel):
    """
    Attributes:
        function: ToolChoiceFunction
        type: Literal["function"]
    """

    function: ToolChoiceFunction
    type: str = "function"

    def __init__(self, name: str):
        super().__init__(function=ToolChoiceFunction(name=name))


class ToolConfig(BaseModel):
    """
    Attributes:
        tools: tools schema
        parallel_tool_calls: bool
        tool_choice: ToolChoice | Literal["none", "auto"]
    """

    tools: List[Dict]
    parallel_tool_calls: Optional[bool] = None
    tool_choice: Optional[Literal["none", "auto"] | ToolChoice] = None


@dataclass
class Model:
    """
    Attributes:
        name: str
        default_provider: ClientType
        provider_name_map: Dict[ClientType, str]
        allowed_providers: Optional[List[ClientType]] = None
        openrouter_providers: List[Optional[OpenRouterProvider]] = None
    """

    name: str  # Our internal reference name
    default_provider: ClientType
    provider_name_map: Dict[ClientType, str]  # Mapping of provider names to model names
    allowed_providers: Optional[List[ClientType]] = None
    openrouter_providers: List[Optional[OpenRouterProvider]] = None


@dataclass
class ClientSetupConfig:
    """
    Attributes:
        client: ClientType
        api_key: str
        project_id: Optional[str] = None
        location: Optional[str] = None
    """

    client: ClientType
    api_key: Optional[str] = None
    project_id: Optional[str] = None  # For Google
    location: Optional[str] = None  # For Google


@dataclass
class ModelInstanceRequest:
    """
    Attributes:
        model_name: str
        provider: Optional[ClientType] = None
        openrouter_provider: Optional[OpenRouterProvider] = None
        model_defaults: Optional[Dict[str, str]] = None
    """

    model_name: str
    provider: Optional[ClientType] = None
    openrouter_provider: Optional[OpenRouterProvider] = None
    model_extras: Optional[Dict[str, str]] = None

    @field_validator("openrouter_provider")
    def validate_openrouter_provider(
        cls, v: Optional[OpenRouterProvider], info
    ) -> Optional[OpenRouterProvider]:
        if v and info.raw.get("provider") != ClientType.OPENROUTER:
            raise ValueError(
                "openrouter_provider can only be set when provider is OPENROUTER"
            )
        return v


@dataclass
class ModelInstance:
    """
    Attributes:
        model: Model
        provider_model_name: str
        provider: ClientType
        openrouter_provider: Optional[OpenRouterProvider] = None
        model_extras: Optional[Dict[str, str]] = None
    """

    model: Model
    provider_model_name: str
    provider: Union["ClientOpenAI", "ClientOpenRouter"]
    openrouter_provider: Optional[List[OpenRouterProvider] | OpenRouterProvider] = None
    model_extras: Optional[Dict[str, Any]] = None
