from typing import List
from abc import ABC, abstractmethod
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
from pydantic import BaseModel

class ResponseWrapper(ABC):
    @property
    @abstractmethod
    def full(self) -> BaseModel:
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
    def __init__(self, response: BaseModel):
        self.data = response

    @property
    def full(self) -> BaseModel:
        return self.data
    
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
