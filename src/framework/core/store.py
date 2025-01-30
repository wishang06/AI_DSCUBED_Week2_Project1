from src.framework.clients.response import ResponseWrapper, ResponseWrapperOpenAI, StreamedResponseWrapperOpenAI
from typing import Dict, Any, List, Optional, Union
from loguru import logger
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall, Function

def surround_with_thinking(text):
    return f"<thinking>{text}</thinking>"

class ContextStore:
    def __init__(self, system_prompt: Optional[str] = None):
        self.response_log: List[Any] = [] # need to define type
        self.chat_history: List[Any] = []
        self.system: str
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = ""
        
    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def store_response(self, response: Union[ResponseWrapperOpenAI, StreamedResponseWrapperOpenAI], role: str):
        self.response_log.append(response)
        if isinstance(response, StreamedResponseWrapperOpenAI):
            if response.response_reasoning:
                self.chat_history.append({"role": role, "content": surround_with_thinking(response.response_reasoning)
                                     + "\n" + response.response_content})
            else:
                self.chat_history.append({"role": role, "content": response.response_content})
        else:
            self.chat_history.append({"role": role, "content": response.content})

    def store_string(self, string: str, role: str):
        self.response_log.append([role, string])
        self.chat_history.append({"role": role, "content": string})

    def store_tool_response(self, response: ResponseWrapper):
        """Store a tool response in the chat history"""
        self.response_log.append(response)
        if isinstance(response, StreamedResponseWrapperOpenAI):
            calls = []
            call = {
                'id': "",
                'type': "",
                'function': "",
                'arguments': ""
            }
            current_id = None
            for delta in response.response_tool_calls_raw:
                if delta.id and (delta.id != current_id and current_id):
                    # there is a new tool call
                    if (not call['id'] or
                            not call['type'] or
                            not call['function'] or
                            not call['arguments']):
                        raise ValueError("Tool call is missing required fields")
                    calls.append(ChatCompletionMessageToolCall(
                        id=call['id'],
                        type=call['type'],
                        function=Function(name=call['function'],
                                          arguments=call['arguments'])
                    ))
                    call = {
                        'id': "",
                        'type': "",
                        'function': "",
                        'arguments': ""
                    }
                    current_id = delta.id
                    call['id'] = delta.id
                if delta.id and not current_id:
                    current_id = delta.id
                    call['id'] = delta.id
                if delta.type:
                    call['type'] = delta.type
                if delta.function:
                    if delta.function.name:
                        call['function'] = delta.function.name
                    if delta.function.arguments:
                        call['arguments'] += delta.function.arguments
                if delta == response.response_tool_calls_raw[-1]:
                    # last tool call
                    if (not call['id'] or
                            not call['type'] or
                            not call['function'] or
                            not call['arguments']):
                        continue
                    calls.append(ChatCompletionMessageToolCall(
                        id=call['id'],
                        type=call['type'],
                        function=Function(name=call['function'],
                                          arguments=call['arguments'])))
            response.response_tool_calls = calls
            self.chat_history.append({
                "role": "assistant",
                "tool_calls": response.response_tool_calls
            })
        else:
            self.chat_history.append(response.full.choices[0].message)
            for tool_call in response.full.choices[0].message.tool_calls:
                logger.info(f"Tool call: {tool_call}")
    
    def store_function_call_result(self, result: Dict):
        """Store function call result in the chat history
        
        Args:
            result: Dictionary containing role, tool_call_id, name, and result
        """
        self.response_log.append(result)
        self.chat_history.append(result)

    def retrieve(self):
        result = self.chat_history.copy()
        if self.system_prompt != "":
            result.insert(0, {"role": "system", "content": self.system_prompt})
        return result
        
    def clear(self):
        self.response_log = []
        self.chat_history = []
        self.system_prompt = ""



class BasicChatContextStore:
    def __init__(self, system_prompt: Optional[str] = None):
        self.response_log: List[Any] = [] # need to define type
        self.chat_history: List[Dict[str, str]] = []
        self.system: str
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = ""
        
    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def store_response(self, response: ResponseWrapper, role: str):
        self.response_log.append(response)
        self.chat_history.append({"role": role, "content": response.content})

    def store_string(self, string: str, role: str):
        self.response_log.append([role, string])
        self.chat_history.append({"role": role, "content": string})
        
    def retrieve(self):
        result = self.chat_history.copy()
        if self.system_prompt != "":
            result.insert(0, {"role": "system", "content": self.system_prompt})
        return result
        
    def clear(self):
        self.response_log = []
        self.chat_history = []
        self.system_prompt = ""
