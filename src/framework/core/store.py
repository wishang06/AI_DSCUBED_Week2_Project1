from src.framework.clients.response import ResponseWrapper
from typing import Dict, Any, List, Optional
from loguru import logger

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

    def store_response(self, response: ResponseWrapper, role: str):
        self.response_log.append(response)
        self.chat_history.append({"role": role, "content": response.content})

    def store_string(self, string: str, role: str):
        self.response_log.append([role, string])
        self.chat_history.append({"role": role, "content": string})

    def store_tool_response(self, response: ResponseWrapper):
        """Store a tool response in the chat history"""
        self.response_log.append(response)
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
