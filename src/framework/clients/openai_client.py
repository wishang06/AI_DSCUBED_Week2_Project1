from .response import ResponseWrapperOpenAI, StreamedResponseWrapperOpenAI
from typing import Optional, List, Dict, Any
from enum import Enum, auto
from src.framework.clients.response import OpenAIReasoningAPIFormat


class ClientOpenAIType(Enum):
    GEMINI = auto()
    OPENAI = auto()
    OPENROUTER = auto()
    DEEPSEEK = auto()

class ClientOpenAI:
    def __init__(self, client,
                 client_type: ClientOpenAIType,
                 client_reasoning_api_format: Optional[OpenAIReasoningAPIFormat] = None):
        # Store the client as an instance attribute
        self.client = client
        self.type = client_type
        self.reasoning_api_format = client_reasoning_api_format

    @classmethod
    def create_gemini(cls, project, location):
        import vertexai
        from google.auth import default
        from google.auth.transport import requests as transport_requests
        # Initialize Vertex AI
        vertexai.init(project=project, location=location)

        # Obtain credentials
        credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_request = transport_requests.Request()
        credentials.refresh(auth_request)

        # Initialize OpenAI client
        base_url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/endpoints/openapi"
        client = openai.OpenAI(
            base_url=base_url,
            api_key=credentials.token  # Use the refreshed token
        )
        # Return an instance of OpenAIWrapper with the initialized client
        return cls(client, ClientOpenAIType.GEMINI)
    
    @classmethod
    def create_openai(cls, api_key):
        import openai
        client = openai.OpenAI(api_key=api_key)
        return cls(client, ClientOpenAIType.OPENAI)

    @classmethod
    def create_openrouter(cls, api_key):
        import openai
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        return cls(client, ClientOpenAIType.OPENROUTER, OpenAIReasoningAPIFormat.OPENROUTER)

    @classmethod
    def create_deepseek(cls, api_key):
        import openai
        client = openai.OpenAI(
            base_url="https://api.deepseek.com",
            api_key=api_key)
        return cls(client, ClientOpenAIType.DEEPSEEK)

    def create_completion_legacy(self, model_name, context):
        response = self.client.chat.completions.create(model=model_name,
                                                   messages=context,
                                                   temperature=1,
                                                   max_tokens=8000,
                                                   )
        return ResponseWrapperOpenAI(response)

    def create_completion(self,
                          model_name: str,
                          context: List[Dict[str, Any]],
                          tools: Optional[List[Dict[str, Any]]] = None,
                          parallel_tool_calls: bool = True,
                          max_tokens: int = 4096,
                          temperature: float = 0.7):

        kwargs = {"model": model_name,
                  "messages": context,
                  "temperature": temperature,
                  "max_tokens": max_tokens,
                  "extra_body": {}}

        if tools:
            kwargs["tools"] = tools
            kwargs["parallel_tool_calls"] = parallel_tool_calls

        response = self.client.chat.completions.create(**kwargs)

        return ResponseWrapperOpenAI(response)

    def create_streaming_completion(self,
                          model_name: str,
                          context: List[Dict[str, Any]],
                          tools: Optional[List[Dict[str, Any]]] = None,
                          parallel_tool_calls: bool = True,
                          max_tokens: int = 4096,
                          temperature: float = 0.7):

        kwargs = {"model": model_name,
                  "messages": context,
                  "temperature": temperature,
                  "max_tokens": max_tokens,
                  "stream": True,
                  "stream_options": {"include_usage": True},
                  "extra_body": {}}

        if tools:
            kwargs["tools"] = tools
            kwargs["parallel_tool_calls"] = parallel_tool_calls

        response = self.client.chat.completions.create(**kwargs)

        return StreamedResponseWrapperOpenAI(response)


class ClientOpenRouter:
    def __init__(self, api_key: str):
        import openai
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key)

    def create_completion(self,
                          model_name: str,
                          context: List[Dict[str, Any]],
                          tools: Optional[List[Dict[str, Any]]] = None,
                          parallel_tool_calls: bool = True,
                          max_tokens: int = 4096,
                          temperature: float = 0.7,
                          show_reasoning: bool = True,
                          providers: Optional[List[str]] = None,
                          allow_fallbacks: bool = False):

        kwargs = {"model": model_name,
                  "messages": context,
                  "temperature": temperature,
                  "max_tokens": max_tokens,
                  "extra_body": {}}

        if show_reasoning:
            kwargs["extra_body"]["include_reasoning"] = show_reasoning

        if providers:
            kwargs["extra_body"]["providers"] = {
                "order": providers,
                "allow_fallbacks": allow_fallbacks
            }

        if not kwargs["extra_body"]:  # If extra_body is empty
            del kwargs["extra_body"]

        if tools:
            kwargs["tools"] = tools
            kwargs["parallel_tool_calls"] = parallel_tool_calls

        response = self.client.chat.completions.create(**kwargs)

        return ResponseWrapperOpenAI(response)

    def create_streaming_completion(self,
                          model_name: str,
                          context: List[Dict[str, Any]],
                          tools: Optional[List[Dict[str, Any]]] = None,
                          parallel_tool_calls: bool = True,
                          max_tokens: int = 4096,
                          temperature: float = 0.7,
                          show_reasoning: bool = True,
                          providers: Optional[List[str]] = None,
                          allow_fallbacks: bool = False,
                          ):

        kwargs = {"model": model_name,
                  "messages": context,
                  "temperature": temperature,
                  "max_tokens": max_tokens,
                  "stream": True,
                  "stream_options": {"include_usage": True},
                  "extra_body": {}}

        if show_reasoning:
            kwargs["extra_body"]["include_reasoning"] = show_reasoning

        if providers:
            kwargs["extra_body"]["providers"] = {
                "order": providers,
                "allow_fallbacks": allow_fallbacks
            }

        if not kwargs["extra_body"]:  # If extra_body is empty
            del kwargs["extra_body"]

        if tools:
            kwargs["tools"] = tools
            kwargs["parallel_tool_calls"] = parallel_tool_calls

        response = self.client.chat.completions.create(**kwargs)

        return StreamedResponseWrapperOpenAI(response, OpenAIReasoningAPIFormat.OPENROUTER)
