from __future__ import annotations

from collections import defaultdict

from framework.clients.response import (
    ResponseWrapperOpenAI,
    StreamedResponseWrapperOpenAI,
)
from typing import Optional, List, Dict, Any, Callable

from ..types.application_events import (
    StreamingApplicationEvent,
    StreamingEventTypes,
    StreamingChunkTypes,
)
from ..types.clients import ClientType
from ..types.models import ModelInstance, ToolConfig
from pydantic import BaseModel

from ..types.utils import dummy_function


class ClientOpenAI:
    def __init__(
        self,
        client,
        client_type: ClientType,
    ):
        # Store the client as an instance attribute
        self.client = client
        self.type = client_type
        self.reasoning_effort = None
        self.client_defaults = {}

    @classmethod
    def create_gemini_vertex(cls, project, location):
        import vertexai
        import openai
        from google.auth import default
        from google.auth.transport import requests as transport_requests

        # Initialize Vertex AI
        vertexai.init(project=project, location=location)

        # Obtain credentials
        credentials, _ = default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        auth_request = transport_requests.Request()
        credentials.refresh(auth_request)

        # Initialize OpenAI client
        base_url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/endpoints/openapi"
        client = openai.OpenAI(
            base_url=base_url,
            api_key=credentials.token,  # Use the refreshed token
        )
        # Return an instance of OpenAIWrapper with the initialized client
        return cls(client, ClientType.GEMINI_VERTEX)

    @classmethod
    def create_gemini(cls, api_key: str):
        import openai

        client = openai.OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1alpha/openai/",
            api_key=api_key,
        )
        return cls(client, ClientType.GEMINI_API)

    @classmethod
    def create_openai(cls, api_key):
        import openai

        client = openai.OpenAI(api_key=api_key)
        return cls(client, ClientType.OPENAI)

    @classmethod
    def create_deepseek(cls, api_key: str):
        import openai

        client = openai.OpenAI(base_url="https://api.deepseek.com", api_key=api_key)
        return cls(client, ClientType.DEEPSEEK)

    def create_completion_legacy_v2(self, model_name, context):
        response = self.client.chat.completions.create(
            model=model_name,
            messages=context,
            temperature=1,
            max_tokens=8000,
        )
        return ResponseWrapperOpenAI(response)

    @classmethod
    def create_openrouter(cls, api_key: str):
        import openai

        client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        return cls(client, ClientType.OPENROUTER)

    def create_completion(
        self,
        model: ModelInstance,
        context: List[Dict[str, Any]],
        tool_config: Optional[ToolConfig] = None,
        schema: Optional[Dict | BaseModel] = None,
        **kwargs,
    ):
        payload = {
            "model": model.provider_model_name,
            "messages": context,
            "tools": tool_config.tools if tool_config else None,
            "parallel_tool_calls": tool_config.parallel_tool_calls
            if tool_config
            else None,
            "tool_choice": tool_config.tool_choice if tool_config else None,
            "response_format": schema if schema else None,
        }
        if model.model_extras:
            payload.update(model.model_extras)
        if kwargs:
            payload.update(kwargs)
        match model.provider.type:
            case ClientType.OPENROUTER:
                payload["extra_body"] = {}
                payload["extra_body"]["include_reasoning"] = True
                if model.openrouter_provider:
                    payload["extra_body"]["providers"] = {
                        "order": model.provider_model_name,
                        "allow_fallbacks": False,
                    }
        # remove None values from payload
        payload = {k: v for k, v in payload.items() if v is not None}

        response = self.client.chat.completions.create(**payload)
        return ResponseWrapperOpenAI(response, self.type)

    def stream_emit(
        self, emitters: List[Callable] | Callable, event: StreamingApplicationEvent
    ):
        emitters_list = emitters if isinstance(emitters, list) else [emitters]
        for emitter in emitters_list:
            emitter(event)

    def stream_completion(
        self,
        model: ModelInstance,
        context: List[Dict[str, Any]],
        emitters: Optional[List[Callable] | Callable] = dummy_function,
        tool_config: Optional[ToolConfig] = None,
        schema: Optional[Dict | BaseModel] = None,
        **kwargs,
    ):
        payload = {
            "model": model.provider_model_name,
            "messages": context,
            "tools": tool_config.tools if tool_config else None,
            "parallel_tool_calls": tool_config.parallel_tool_calls
            if tool_config
            else None,
            "tool_choice": tool_config.tool_choice if tool_config else None,
            "response_format": schema if schema else None,
            "stream_options": {"include_usage": True},
        }
        if model.model_extras:
            payload.update(model.model_extras)
        if kwargs:
            payload.update(kwargs)
        match model.provider.type:
            case ClientType.OPENROUTER:
                payload["extra_body"] = {}
                payload["extra_body"]["include_reasoning"] = True
                if model.openrouter_provider:
                    payload["extra_body"]["providers"] = {
                        "order": model.provider_model_name,
                        "allow_fallbacks": False,
                    }
        # remove None values from payload
        payload = {k: v for k, v in payload.items() if v is not None}

        chunks = []
        buffer_store = defaultdict(str)

        self.stream_emit(
            emitters, StreamingApplicationEvent(StreamingEventTypes.STARTED)
        )
        with self.client.beta.chat.completions.stream(**payload) as stream:
            for event in stream:
                chunks.append(event)
                match event.type:
                    case "chunk":
                        try:
                            reasoning = event.chunk.choices[0].delta.reasoning
                            if reasoning:
                                buffer_store["reasoning"] += reasoning
                                self.stream_emit(
                                    emitters,
                                    StreamingApplicationEvent(
                                        StreamingEventTypes.CHUNK,
                                        StreamingChunkTypes.REASONING,
                                        {"delta": reasoning, "full": buffer_store},
                                    ),
                                )
                        except (AttributeError, IndexError):
                            pass
                    case "content.delta":
                        buffer_store["content"] += event.delta
                        self.stream_emit(
                            emitters,
                            StreamingApplicationEvent(
                                StreamingEventTypes.CHUNK,
                                StreamingChunkTypes.TEXT,
                                {"delta": event.delta, "full": buffer_store},
                            ),
                        )
                    case "tool_calls.function.arguments.delta":
                        buffer_store["tool_call"] += event.arguments_delta
                        self.stream_emit(
                            emitters,
                            StreamingApplicationEvent(
                                StreamingEventTypes.CHUNK,
                                StreamingChunkTypes.TOOL,
                                {"delta": event.arguments_delta, "full": buffer_store},
                            ),
                        )
        self.stream_emit(
            emitters, StreamingApplicationEvent(StreamingEventTypes.COMPLETED)
        )
        response = stream.get_final_completion()
        return ResponseWrapperOpenAI(response, model.provider.type, chunks)

    def create_completion_legacy(
        self,
        model_name: str,
        context: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        parallel_tool_calls: bool = True,
        tool_choice: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        show_reasoning: bool = True,
    ):
        kwargs = {
            "model": model_name,
            "messages": context,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "extra_body": {},
        }

        if self.reasoning_effort:
            if model_name != "o1-mini-2024-09-12":
                kwargs["reasoning_effort"] = self.reasoning_effort
            kwargs["messages"].pop(0)  # System prompt not supported
            kwargs.pop("max_tokens")
            kwargs.pop("temperature")

        if tools:
            kwargs["tools"] = tools
            kwargs["parallel_tool_calls"] = parallel_tool_calls

        response = self.client.chat.completions.create(**kwargs)

        return ResponseWrapperOpenAI(response, self.reasoning_api_format)

    def create_streaming_completion(
        self,
        model_name: str,
        context: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        parallel_tool_calls: bool = True,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ):
        kwargs = {
            "model": model_name,
            "messages": context,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            "stream_options": {"include_usage": True},
            "extra_body": {},
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["parallel_tool_calls"] = parallel_tool_calls

        response = self.client.chat.completions.create(**kwargs)

        return StreamedResponseWrapperOpenAI(response, self.reasoning_api_format)
