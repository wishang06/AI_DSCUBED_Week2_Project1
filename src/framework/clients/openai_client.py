from src.framework.clients.response import ResponseWrapperOpenAI, StreamedResponseWrapperOpenAI
from typing import Optional, List, Dict, Any
from enum import Enum, auto

from src.framework.types.clients import ClientType, OpenAIReasoningAPIFormat

class OpenAIReasoningEffort(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ClientOpenAI:
    def __init__(self, client,
                 client_type: ClientType,
                 client_reasoning_api_format: Optional[OpenAIReasoningAPIFormat] = None):
        # Store the client as an instance attribute
        self.client = client
        self.type = client_type
        self.reasoning_effort = None
        self.reasoning_api_format = client_reasoning_api_format

    @classmethod
    def create_gemini_vertex(cls, project, location):
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
        return cls(client, ClientType.GEMINI_VERTEX)

    @classmethod
    def create_gemini(cls, api_key: str):
        import openai
        client = openai.OpenAI(base_url="https://generativelanguage.googleapis.com/v1alpha/openai/",
                               api_key=api_key)
        return cls(client, ClientType.GEMINI_API)

    @classmethod
    def create_openai(cls, api_key):
        import openai
        client = openai.OpenAI(api_key=api_key)
        return cls(client, ClientType.OPENAI)

    @classmethod
    def create_deepseek(cls, api_key: str):
        import openai
        client = openai.OpenAI(
            base_url="https://api.deepseek.com",
            api_key=api_key)
        return cls(client, ClientType.DEEPSEEK)

    def create_completion_legacy(self, model_name, context):
        response = self.client.chat.completions.create(model=model_name,
                                                   messages=context,
                                                   temperature=1,
                                                   max_tokens=8000,
                                                   )
        return ResponseWrapperOpenAI(response)

    def toggle_openai_reasoning(self, reasoning_effort: OpenAIReasoningEffort):
        """
        Set the reasoning effort for the OpenAI client
        :param reasoning_effort: The reasoning effort to set

        To turn off reasoning, set reasoning_effort to None
        """
        self.reasoning_effort = reasoning_effort
        self.reasoning_api_format = None # Reset the reasoning API format

    def create_completion(self,
                          model_name: str,
                          context: List[Dict[str, Any]],
                          tools: Optional[List[Dict[str, Any]]] = None,
                          parallel_tool_calls: bool = True,
                          max_tokens: int = 4096,
                          temperature: float = 0.7,
                          show_reasoning: bool = True):

        kwargs = {"model": model_name,
                  "messages": context,
                  "temperature": temperature,
                  "max_tokens": max_tokens,
                  "extra_body": {}}

        if self.reasoning_effort:
            kwargs["reasoning_effort"] = self.reasoning_effort

        if tools:
            kwargs["tools"] = tools
            kwargs["parallel_tool_calls"] = parallel_tool_calls

        response = self.client.chat.completions.create(**kwargs)

        return ResponseWrapperOpenAI(response, self.reasoning_api_format)

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

        return StreamedResponseWrapperOpenAI(response, self.reasoning_api_format)
