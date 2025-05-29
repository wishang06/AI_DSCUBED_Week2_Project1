import uuid
from typing import Any, Dict, List, Literal, Optional, Union

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from prompt_toolkit import Application

from llmgine.bus.bus import MessageBus
from llmgine.llm.providers import LLMProvider
from llmgine.llm.providers.events import LLMCallEvent, LLMResponseEvent
from llmgine.llm.providers.providers import Providers
from llmgine.llm.providers.response import LLMResponse, ResponseTokens
from llmgine.llm.tools.toolCall import ToolCall
from llmgine.llm import ToolChoiceOrDictType

OpenRouterProviders = Literal[
    "OpenAI",
    "Anthropic",
    "Google",
    "Google AI Studio",
    "Amazon Bedrock",
    "Groq",
    "SambaNova",
    "Cohere",
    "Mistral",
    "Together",
    "Together 2",
    "Fireworks",
    "DeepInfra",
    "Lepton",
    "Novita",
    "Avian",
    "Lambda",
    "Azure",
    "Modal",
    "AnyScale",
    "Replicate",
    "Perplexity",
    "Recursal",
    "OctoAI",
    "DeepSeek",
    "Infermatic",
    "AI21",
    "Featherless",
    "Inflection",
    "xAI",
    "Cloudflare",
    "SF Compute",
    "Minimax",
    "Nineteen",
    "Liquid",
    "Stealth",
    "NCompass",
    "InferenceNet",
    "Friendli",
    "AionLabs",
    "Alibaba",
    "Nebius",
    "Chutes",
    "Kluster",
    "Crusoe",
    "Targon",
    "Ubicloud",
    "Parasail",
    "Phala",
    "Cent-ML",
    "Venice",
    "OpenInference",
    "Atoma",
    "01.AI",
    "HuggingFace",
    "Mancer",
    "Mancer 2",
    "Hyperbolic",
    "Hyperbolic 2",
    "Lynn 2",
    "Lynn",
    "Reflection",
]


class OpenRouterResponse(LLMResponse):
    def __init__(self, response: ChatCompletion) -> None:
        self.response = response

    @property
    def raw(self) -> ChatCompletion:
        return self.response

    @property
    def content(self) -> str:
        return self.response.choices[0].message.content

    @property
    def tool_calls(self) -> List[ToolCall]:
        return [
            ToolCall(tool_call)
            for tool_call in self.response.choices[0].message.tool_calls
        ]

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0

    @property
    def finish_reason(self) -> str:
        return self.response.choices[0].finish_reason

    @property
    def tokens(self) -> ResponseTokens:
        return ResponseTokens(
            prompt_tokens=self.response.usage.prompt_tokens,
            completion_tokens=self.response.usage.completion_tokens,
            total_tokens=self.response.usage.total_tokens,
        )

    @property
    def reasoning(self) -> str:
        return self.response.choices[0].message.reasoning


class OpenRouterProvider(LLMProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
        provider: Optional[OpenRouterProviders] = None,
        model_component_id: Optional[str] = None,
    ) -> None:
        self.model = model
        self.model_component_id = model_component_id
        self.provider = provider
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = AsyncOpenAI(api_key=api_key, base_url=self.base_url)
        self.bus = MessageBus()

    async def generate(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        tool_choice: ToolChoiceOrDictType = "auto",
        temperature: float = 0.7,
        max_completion_tokens: int = 5068,
        response_format: Optional[Dict] = None,
        reasoning: bool = False,
        reasoning_max_tokens: Optional[int] = None,
        reasoning_effort: Optional[Literal["low", "medium", "high"]] = None,
        reasoning_include_reasoning: Optional[bool] = False,
        retry_count: int = 1,
        test: bool = False,
        **kwargs: Any,
    ) -> LLMResponse:
        call_id = str(uuid.uuid4())

        # Default payload
        payload = {
            "model": self.model,
            "messages": messages,
            "max_completion_tokens": max_completion_tokens,
        }

        # Provider specific
        if self.provider:
            payload["extra_body"] = {
                "provider": {
                    "order": [self.provider],
                    "allow_fallbacks": False,
                    "data_collection": "deny",
                }
            }

        # Temperature
        if temperature:
            payload["temperature"] = temperature

        # Tools
        if tools:
            payload["tools"] = tools

            if tool_choice:
                payload["tool_choice"] = tool_choice

        # Response format
        if response_format:
            payload["response_format"] = response_format

        # Reasoning
        if reasoning_effort:
            payload["reasoning_effort"] = reasoning_effort

        # Reasoning
        if reasoning:
            payload["extra_body"]["reasoning"] = {}
            if reasoning_max_tokens:
                payload["extra_body"]["reasoning"]["max_tokens"] = reasoning_max_tokens
            if reasoning_effort:
                payload["extra_body"]["reasoning"]["effort"] = reasoning_effort
            if not reasoning_include_reasoning:
                payload["extra_body"]["reasoning"]["exclude"] = True

        # Update payload with additional kwargs
        payload.update(**kwargs)  # type: ignore

        # Call event
        call_event = LLMCallEvent(
            call_id=call_id,
            model_id=self.model_component_id,
            provider=Providers.OPENROUTER,
            payload=payload,
        )
        await self.bus.publish(call_event)
        for _ in range(retry_count):
            try:
                response = await self.client.chat.completions.create(**payload)
                break
            except Exception as e:
                await self.bus.publish(
                    LLMResponseEvent(
                        call_id=call_id,
                        error=e,
                    )
                )
        await self.bus.publish(
            LLMResponseEvent(
                call_id=call_id,
                raw_response=response,
            )
        )
        if test:
            # Return raw response
            return response
        else:
            # Return wrapped response
            return OpenRouterResponse(response)

    def stream() -> None:
        # TODO: Implement streaming
        raise NotImplementedError("Streaming is not supported for OpenRouter")


async def main():
    from llmgine.bootstrap import ApplicationBootstrap, ApplicationConfig
    import os
    from llmgine.llm.tools import ToolManager

    def get_weather(city: str) -> str:
        """
        Get the weather in a city.

        Args:
            city: The city to get the weather for.

        Returns:
            str: The weather in the city.
        """
        return f"The weather in {city} is sunny with a chance to rain meatballs."

    app = ApplicationBootstrap(ApplicationConfig(enable_console_handler=False))
    await app.bootstrap()
    tool_manager = ToolManager(session_id="test", engine_id="test")
    await tool_manager.register_tool(get_weather)
    provider = OpenRouterProvider(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model="deepseek/deepseek-chat-v3-0324",
        provider="Fireworks",
    )
    tools = await tool_manager.get_tools()
    response = await provider.generate(
        messages=[{"role": "user", "content": "Whats the weather in Tokyo?"}],
        tools=tools,
        test=True,
    )
    print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
