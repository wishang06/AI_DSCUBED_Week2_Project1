from typing import AsyncGenerator, Generator, Optional, Dict, Any
from openai.types.chat import ChatCompletionChunk, ChatCompletion
from src.framework.clients.response import ResponseWrapper
from src.framework.core.store import ContextStore
from src.framework.core.observer import EngineSubject, Observer
from src.framework.clients.openai_client import ClientOpenAI


class StreamingResponseWrapper(ResponseWrapper):
    """Wrapper for streaming responses"""

    def __init__(self, response: ChatCompletionChunk):
        self.data = response

    @property
    def full(self) -> ChatCompletionChunk:
        return self.data

    @property
    def content(self) -> str:
        return self.data.choices[0].delta.content or ""

    @property
    def tool_calls(self) -> list:
        if hasattr(self.data.choices[0].delta, 'tool_calls'):
            return self.data.choices[0].delta.tool_calls
        return []

    @property
    def stop_reason(self) -> Optional[str]:
        return self.data.choices[0].finish_reason

    @property
    def tokens_input(self) -> int:
        # Not available in streaming response
        return 0

    @property
    def tokens_output(self) -> int:
        # Not available in streaming response
        return 0

    @property
    def to_json(self) -> str:
        return self.data.model_dump_json()


class StreamingClientOpenAI(ClientOpenAI):
    """Extension of OpenAI client with streaming capabilities"""

    async def create_streaming_completion(
            self,
            model_name: str,
            context: list,
            tools: Optional[list] = None,
    ) -> AsyncGenerator[StreamingResponseWrapper, None]:
        """Create a streaming completion"""
        kwargs = {
            "model": model_name,
            "messages": context,
            "temperature": 1,
            "max_tokens": 8000,
            "top_p": 1,
            "stream": True
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        async for chunk in await self.client.chat.completions.create(**kwargs):
            yield StreamingResponseWrapper(chunk)


class StreamingEngine:
    """Engine that supports streaming LLM responses"""

    def __init__(
            self,
            client: StreamingClientOpenAI,
            model_name: str,
            tools: Optional[list] = None,
            system_prompt: Optional[str] = None,
    ):
        self.client = client
        self.model_name = model_name
        self.tools = tools or []
        self.store = ContextStore()
        self.subject = EngineSubject()

        if system_prompt:
            self.store.set_system_prompt(system_prompt)

    def subscribe(self, observer: Observer):
        """Add an observer to the engine"""
        self.subject.register(observer)

    async def stream_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """Stream a response for a given prompt"""
        # Store user prompt
        self.store.store_string(prompt, "user")

        # Initialize accumulated response
        accumulated_response = ""
        accumulated_tool_calls = []
        current_tool_call = None

        # Notify observers that streaming is starting
        self.subject.notify({
            "type": "stream_start",
            "message": "Starting response stream..."
        })

        try:
            # Get streaming response
            async for chunk in await self.client.create_streaming_completion(
                    self.model_name,
                    self.store.retrieve(),
                    tools=self.tools
            ):
                # Handle tool calls if present
                if chunk.tool_calls:
                    for tool_call in chunk.tool_calls:
                        if not current_tool_call or tool_call.index != current_tool_call.index:
                            if current_tool_call:
                                accumulated_tool_calls.append(current_tool_call)
                            current_tool_call = tool_call
                        else:
                            # Merge with current tool call
                            if hasattr(tool_call, 'function'):
                                if hasattr(tool_call.function, 'name'):
                                    current_tool_call.function.name += tool_call.function.name
                                if hasattr(tool_call.function, 'arguments'):
                                    current_tool_call.function.arguments += tool_call.function.arguments

                # Handle content if present
                if chunk.content:
                    accumulated_response += chunk.content
                    yield chunk.content

                # Handle end of response
                if chunk.stop_reason:
                    if current_tool_call:
                        accumulated_tool_calls.append(current_tool_call)
                    break

        finally:
            # Store the complete response
            if accumulated_response:
                self.store.store_string(accumulated_response, "assistant")

            # Handle any accumulated tool calls
            if accumulated_tool_calls:
                self.subject.notify({
                    "type": "tool_calls",
                    "tool_calls": accumulated_tool_calls
                })

            # Notify observers that streaming is complete
            self.subject.notify({
                "type": "stream_end",
                "message": "Stream completed"
            })


class StreamingObserver(Observer):
    """Observer for handling streaming updates"""

    def __init__(self, display_class):
        self.display = display_class(title="LLM Response")
        self.current_stream = None

    def update(self, event: Dict[str, Any]):
        """Handle various streaming events"""
        if event["type"] == "stream_start":
            # Initialize new stream display
            self.current_stream = ""
        elif event["type"] == "content":
            # Update display with new content
            self.current_stream += event["content"]
            self.display.update_content(self.current_stream)
        elif event["type"] == "tool_calls":
            # Handle tool calls
            self.display.show_tool_calls(event["tool_calls"])
        elif event["type"] == "stream_end":
            # Finalize display
            self.display.finish_stream()

    def get_input(self, event: Any) -> str:
        """Handle input requests if needed"""
        return ""
