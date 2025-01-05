from typing import List, Callable, Dict, Optional
import inspect
import json

def openai_function_wrapper(
    function_description: str,
    parameter_descriptions: Dict[str, str] = {},
) -> Callable:
    def decorator(func: Callable) -> Callable:
        class FunctionWrapper:
            def __init__(self, func, function_description, parameter_descriptions):
                self.func = func
                self.function_description = function_description
                self.parameter_descriptions = parameter_descriptions
                self.output = {
                    "type": "function",
                    "function": {
                        "name": func.__name__,
                        "description": self.function_description,
                        "parameters": {
                            "type": "object",
                            "required": [],
                            "properties": {},
                            "additionalProperties": False,
                        },
                    },
                }
                self._inspect_parameters()

            def __call__(self, *args, **kwargs):
                return self.func(*args, **kwargs)

            def _inspect_parameters(self):
                signature = inspect.signature(self.func)
                for name, param in signature.parameters.items():
                    param_info = {
                        "description": self.parameter_descriptions.get(name, ""),
                        "type": self._get_param_type(param),
                    }
                    self.output["function"]["parameters"]["properties"][
                        name
                    ] = param_info
                    if param.default == inspect.Parameter.empty:
                        self.output["function"]["parameters"]["required"].append(name)

            def _get_param_type(self, param):
                # Basic type mapping
                if param.annotation is inspect.Parameter.empty:
                    return "string"
                elif param.annotation is str:
                    return "string"
                elif param.annotation is int:
                    return "integer"
                elif param.annotation is float:
                    return "number"
                elif param.annotation is bool:
                    return "boolean"
                elif param.annotation is list:
                    return "array"
                else:
                    return "string"

        return FunctionWrapper(func, function_description, parameter_descriptions)

    return decorator

def create_tools_schema(functions: List[callable]) -> List:
    tools = []
    for function in functions:
        tools.append(function.output)
    return tools

def create_tools_lookup(functions: List[callable]) -> List:
    tools_lookup = {} 
    for function in functions:
        tools_lookup[function.func.__name__] = function
    return tools_lookup

def parse_functions(tool_calls):
    """Parse function calls from tool_calls list
    
    Args:
        tool_calls: List of tool call objects from the response
        
    Returns:
        List of function call objects
    """
    functions = []
    if tool_calls:
        for tool in tool_calls:
            if tool.type == "function":
                functions.append(tool)
    return functions

def execute_function(function_object, tools_lookup):
    function = tools_lookup[function_object.function.name]
    kwargs = json.loads(function_object.function.arguments) 
    result = function(**kwargs)
    return result
