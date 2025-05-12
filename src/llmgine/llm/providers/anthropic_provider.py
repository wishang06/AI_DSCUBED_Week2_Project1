"""OpenAI provider implementation."""

from typing import Any, Dict, List, Literal, Optional, Union
import uuid

from llmgine.bootstrap import ApplicationConfig
from llmgine.llm.providers.events import LLMCallEvent, LLMResponseEvent
from llmgine.llm.providers.providers import Providers
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from llmgine.bus.bus import MessageBus
from llmgine.llm.providers import LLMProvider
from llmgine.llm.providers.response import LLMResponse, ResponseTokens
from llmgine.llm.tools.types import ToolCall

from anthropic import AsyncAnthropic


class AnthropicResponse(LLMResponse):
    def __init__(self, response: ChatCompletion) -> None:
        self.response = response

    @property
    def raw(self) -> ChatCompletion:
        return self.response

    @property
    def content(self) -> str:
        return self.response.content[0].text

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


class AnthropicProvider(LLMProvider):
    def __init__(
        self, api_key: str, model: str, model_component_id: Optional[str] = None
    ) -> None:
        self.model = model
        self.model_component_id = model_component_id
        self.client = AsyncAnthropic(api_key=api_key)
        self.bus = MessageBus()

    async def generate(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        tool_choice: Union[Literal["auto", "none", "required"], Dict] = "auto",
        parallel_tool_calls: Optional[bool] = None,
        temperature: Optional[float] = None,
        max_completion_tokens: int = 5068,
        response_format: Optional[Dict] = None,
        thinking_enabled: bool = False,
        thinking_budget: Optional[int] = None,
        test: bool = False,
        **kwargs: Any,
    ) -> LLMResponse:
        call_id = str(uuid.uuid4())

        # construct the payload
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_completion_tokens,
        }

        # System prompt extract
        if messages[0]["role"] == "system":
            payload["system"] = messages[0]["content"]
            payload["messages"] = messages[1:]

        if temperature:
            payload["temperature"] = temperature

        if tools:
            payload["tools"] = tools

            if tool_choice:
                payload["tool_choice"] = tool_choice

            if parallel_tool_calls is not None:
                payload["parallel_tool_calls"] = parallel_tool_calls

        if response_format:
            payload["response_format"] = response_format

        if thinking_enabled:
            payload["thinking"] = {
                "type": "enabled",
                "budget": thinking_budget,
            }

        payload.update(**kwargs)
        call_event = LLMCallEvent(
            call_id=call_id,
            model_id=self.model_component_id,
            provider=Providers.ANTHROPIC,
            payload=payload,
        )
        await self.bus.publish(call_event)
        try:
            response = await self.client.messages.create(**payload)
        except Exception as e:
            await self.bus.publish(
                LLMResponseEvent(
                    call_id=call_id,
                    error=e,
                )
            )
            raise e
        await self.bus.publish(
            LLMResponseEvent(
                call_id=call_id,
                raw_response=response,
            )
        )
        if test:
            return response
        else:
            return AnthropicResponse(response)

    def stream():
        # TODO: Implement streaming
        raise NotImplementedError("Streaming is not supported for OpenAI")

async def main():
    import dotenv
    import os
    from llmgine.bootstrap import ApplicationBootstrap
    dotenv.load_dotenv(override=True)
    app = ApplicationBootstrap(ApplicationConfig(enable_console_handler=False))
    await app.bootstrap()
    provider = AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY"), model="claude-3-5-sonnet-20240620")
    response = await provider.generate(messages=[{"role": "system", "content": "Respond in pirate language"}, {"role": "user", "content": "Hello, how are you?"}])
    print(response.content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())