from typing import List, Any, Optional, Callable
from abc import ABC, abstractmethod
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
from pyasn1.type.univ import Boolean
from pydantic import BaseModel
from dataclasses import dataclass, field
from enum import Enum, auto
import openai

class OpenAIReasoningAPIFormat(Enum):
    OPENROUTER = auto()
    DEEPSEEK = auto()


class StreamedResponseStatus(Enum):
    CREATED = auto()
    REASONING = auto()
    GENERATING = auto()
    COMPLETED_WITH_CONTENT = auto()
    COMPLETED_WITH_TOOL_CALLS = auto()
    INTERRUPTED = auto()
    FAILED = auto()

class ResponseWrapper(ABC):
    @property
    @abstractmethod
    def full(self) -> Any:
        pass

    @property
    @abstractmethod
    def stop_reason(self) -> str:
        pass

    @property
    @abstractmethod
    def reasoning(self) -> str:
        pass

    @property
    @abstractmethod
    def content(self) -> str:
        pass

    @property
    @abstractmethod
    def tool_calls(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def tokens_input(self) -> int:
        pass

    @property
    @abstractmethod
    def tokens_output(self) -> int:
        pass

    @property
    @abstractmethod
    def to_json(self) -> str:
        pass

class ResponseWrapperOpenAI(ResponseWrapper):
    def __init__(self, response: BaseModel, reasoning_api_format: Optional[OpenAIReasoningAPIFormat] = None):
        self.data = response
        if reasoning_api_format is None:
            self.get_reasoning_content = lambda x: None
        elif reasoning_api_format == OpenAIReasoningAPIFormat.OPENROUTER:
            self.get_reasoning_content = lambda x: x.choices[0].message.reasoning if hasattr(x.choices[0].message, 'reasoning') else None
        elif reasoning_api_format == OpenAIReasoningAPIFormat.DEEPSEEK:
            self.get_reasoning_content = lambda x: x.choices[0].message.reasoning_content if hasattr(x.choices[0], 'reasoning_content') else None

    @property
    def full(self) -> BaseModel:
        return self.data

    @property
    def reasoning(self) -> str:
        return self.get_reasoning_content(self.data)

    @property
    def content(self) -> str:
        return self.data.choices[0].message.content if self.data.choices[0].message.content else ""
    
    @property
    def tool_calls(self) -> List[ChatCompletionMessageToolCall]:
        message = self.data.choices[0].message
        return message.tool_calls if hasattr(message, 'tool_calls') else []
    
    @property
    def stop_reason(self) -> str:
        return self.data.choices[0].finish_reason

    @property
    def tokens_input(self) -> int:
        return self.data.usage.prompt_tokens
    
    @property
    def tokens_output(self) -> int:
        return self.data.usage.completion_tokens
    
    @property
    def to_json(self) -> str:
        return self.data.to_json()


@dataclass
class ResponseTokenStats:
    prompt_tokens: int = 0
    reasoning_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    time_till_first_token: float = 0.0  # not implemented
    tokens_per_second: float = 0.0  # not implemented
    total_time_taken: float = 0.0  # not implemented

    def calculate_total_tokens(self):
        self.total_tokens = self.reasoning_tokens + self.completion_tokens


@dataclass
class StreamedResponseWrapperOpenAI:
    # parameters
    response: Any  # Stream of ChatCompletionChunks
    reasoning_api_format: Optional[OpenAIReasoningAPIFormat] = None

    # internal state
    response_reasoning: str = field(default="", init=False)
    response_content: str = field(default="", init=False)
    response_tool_calls: List[ChatCompletionMessageToolCall] = field(default_factory=list, init=False)
    chunks: List[BaseModel] = field(default_factory=list, init=False)
    usage: ResponseTokenStats = field(default_factory=ResponseTokenStats, init=False)
    status: StreamedResponseStatus = field(default=StreamedResponseStatus.CREATED, init=False)

    def __post_init__(self):
        """Initialize the iterator and reasoning content handler"""
        self.iter = self.response.__iter__()

        # Set up reasoning content handler based on API format
        if self.reasoning_api_format is None:
            self.get_reasoning_content = lambda x: None
        elif self.reasoning_api_format == OpenAIReasoningAPIFormat.OPENROUTER:
            self.get_reasoning_content = lambda x: x.choices[0].delta.reasoning if hasattr(x.choices[0].delta,
                                                                                           'reasoning') else None
        elif self.reasoning_api_format == OpenAIReasoningAPIFormat.DEEPSEEK:
            self.get_reasoning_content = lambda x: x.choices[0].delta.reasoning_content if hasattr(x.choices[0].delta,
                                                                                                   'reasoning_content') else None
        else:
            raise ValueError(f"Invalid reasoning API format: {self.reasoning_api_format}")

    def __iter__(self):
        """Make the class iterable"""
        return self

    def __next__(self) -> BaseModel:
        """Process the next chunk in the stream"""
        try:
            chunk = next(self.iter)
            self.chunks.append(chunk)
            delta = chunk.choices[0].delta

            # Handle reasoning content if present
            reasoning_content = self.get_reasoning_content(chunk)
            if reasoning_content:
                self.response_reasoning += reasoning_content
                self.status = StreamedResponseStatus.REASONING

            # Handle regular content
            if hasattr(delta, 'content') and delta.content:
                self.response_content += delta.content
                self.status = StreamedResponseStatus.GENERATING

            # Handle tool calls
            if hasattr(delta, 'tool_calls') and delta.tool_calls:
                self.response_tool_calls.extend(delta.tool_calls)
                self.status = StreamedResponseStatus.COMPLETED_WITH_TOOL_CALLS

            # Handle completion
            if chunk.choices[0].finish_reason:
                if self.response_tool_calls:
                    self.status = StreamedResponseStatus.COMPLETED_WITH_TOOL_CALLS
                else:
                    self.status = StreamedResponseStatus.COMPLETED_WITH_CONTENT

            return chunk

        except (StopIteration, IndexError) as e:
            # Update usage statistics if available
            if self.chunks and hasattr(self.chunks[-1], 'usage'):
                self.usage = self.chunks[-1].usage
            raise StopIteration

        except openai.APIError as e:
            self.status = StreamedResponseStatus.FAILED
            raise

        except Exception as e:
            self.status = StreamedResponseStatus.INTERRUPTED
            raise

    @property
    def stop_reason(self) -> str:
        """Get the stop reason from the last chunk"""
        if not self.chunks:
            return ""
        try:
            stop_reason = self.chunks[-2].choices[0].finish_reason
            return stop_reason
        except IndexError:
            raise ValueError("No stop reason available")

    @property
    def content(self) -> str:
        """Get accumulated content"""
        return self.response_content

    @property
    def reasoning(self) -> str:
        """Get accumulated reasoning content"""
        return self.response_reasoning

    @property
    def tool_calls(self) -> List[ChatCompletionMessageToolCall]:
        """Get accumulated tool calls"""
        return self.response_tool_calls

    @property
    def tokens_input(self) -> int:
        """Get input token count"""
        return self.usage.prompt_tokens

    @property
    def tokens_output(self) -> int:
        """Get output token count"""
        return self.usage.completion_tokens

    @property
    def full(self) -> Any:
        """Get full response data"""
        return self

    @property
    def to_json(self) -> str:
        """Convert response to JSON string"""
        # Implement this based on your needs
        return "JSON serialization not implemented"
