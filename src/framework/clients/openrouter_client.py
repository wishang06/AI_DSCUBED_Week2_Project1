from typing import List, Dict, Any, Optional, Union

from src.framework.clients.response import ResponseWrapperOpenAI, StreamedResponseWrapperOpenAI
from src.framework.types.clients import OpenAIReasoningAPIFormat, ClientType
from src.framework.types.openrouter_providers import OpenRouterProvider

class ClientOpenRouter:

    def __init__(self, api_key: str):
        import openai
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key)
        self.provider_model_store: Dict[str, List[OpenRouterProvider]] = {}
        self.type = ClientType.OPENROUTER

    def set_model_providers(self, model: str,
                            providers: Union[OpenRouterProvider, List[OpenRouterProvider]],
                            ):
        self.provider_model_store[model] = providers if isinstance(providers, list) else [providers]

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

        if show_reasoning:
            kwargs["extra_body"]["include_reasoning"] = show_reasoning

        if model_name in self.provider_model_store and self.provider_model_store[model_name]:
            kwargs["extra_body"]["providers"] = {
                "order": self.provider_model_store[model_name],
                "allow_fallbacks": False
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

        if model_name in self.provider_model_store and self.provider_model_store[model_name]:
            kwargs["extra_body"]["providers"] = {
                "order": self.provider_model_store[model_name],
                "allow_fallbacks": False
            }

        if not kwargs["extra_body"]:  # If extra_body is empty
            del kwargs["extra_body"]

        if tools:
            kwargs["tools"] = tools
            kwargs["parallel_tool_calls"] = parallel_tool_calls

        response = self.client.chat.completions.create(**kwargs)

        return StreamedResponseWrapperOpenAI(response, OpenAIReasoningAPIFormat.OPENROUTER)
