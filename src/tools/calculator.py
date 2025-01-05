import math
from typing import Union, Dict
from functools import wraps
from src.tool_calling.tool_calling import openai_function_wrapper

def validate_numbers(*args):
    """Decorator to validate numeric inputs"""
    def decorator(func):
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            processed_args = []
            for arg in func_args:
                try:
                    processed_args.append(float(arg))
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid argument type: {type(arg)}. Expected number.")
            return func(*processed_args, **func_kwargs)
        return wrapper
    return decorator

class Calculator:
    """Calculator tool for basic and advanced mathematical operations"""
    
    @staticmethod
    @openai_function_wrapper(
        function_description="Add two numbers together",
        parameter_descriptions={
            "a": "First number",
            "b": "Second number"
        }
    )
    @validate_numbers(2)
    def add(a: Union[int, float], b: Union[int, float]) -> float:
        """Add two numbers"""
        return float(float(a) + float(b))
    
    @staticmethod
    @openai_function_wrapper(
        function_description="Subtract second number from first number",
        parameter_descriptions={
            "a": "First number",
            "b": "Second number to subtract"
        }
    )
    @validate_numbers(2)
    def subtract(a: Union[int, float], b: Union[int, float]) -> float:
        """Subtract b from a"""
        return float(float(a) - float(b))
    
    @staticmethod
    @openai_function_wrapper(
        function_description="Multiply two numbers together",
        parameter_descriptions={
            "a": "First number",
            "b": "Second number"
        }
    )
    @validate_numbers(2)
    def multiply(a: Union[int, float], b: Union[int, float]) -> float:
        """Multiply two numbers"""
        return float(float(a) * float(b))
    
    @staticmethod
    @openai_function_wrapper(
        function_description="Divide first number by second number",
        parameter_descriptions={
            "a": "Number to be divided",
            "b": "Number to divide by"
        }
    )
    @validate_numbers(2)
    def divide(a: Union[int, float], b: Union[int, float]) -> float:
        """Divide a by b"""
        if float(b) == 0:
            raise ValueError("Cannot divide by zero")
        return float(float(a) / float(b))
    
    @staticmethod
    @openai_function_wrapper(
        function_description="Calculate the square root of a number",
        parameter_descriptions={
            "a": "Number to calculate square root of"
        }
    )
    @validate_numbers(1)
    def square_root(a: Union[int, float]) -> float:
        """Calculate square root of a number"""
        a = float(a)
        if a < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return float(math.sqrt(a))
    
    @staticmethod
    @openai_function_wrapper(
        function_description="Calculate base raised to the power of exponent",
        parameter_descriptions={
            "base": "Base number",
            "exponent": "Power to raise the base to"
        }
    )
    @validate_numbers(2)
    def power(base: Union[int, float], exponent: Union[int, float]) -> float:
        """Calculate base raised to the power of exponent"""
        return float(math.pow(float(base), float(exponent)))
