import pytest
from src.framework.tool_calling import (
    openai_function_wrapper,
    create_tools_schema,
    create_tools_lookup,
    execute_function,
    ToolManager
)
from src.framework.clients import ClientOpenAI
from src.framework.setup import OPENAI_API_KEY
from openai import OpenAI
import json
from typing import Dict, Any

# Test fixtures
@pytest.fixture
def openai_client():
    return ClientOpenAI.create_openai(OPENAI_API_KEY)

@pytest.fixture
def raw_openai_client():
    return OpenAI(api_key=OPENAI_API_KEY)

# Test tools
@openai_function_wrapper(
    funct_descript="Add two numbers",
    param_descriptions={"a": "First number", "b": "Second number"},
    required_parameters=["a", "b"]
)
def add(a: int, b: int) -> int:
    return a + b

@openai_function_wrapper(
    funct_descript="Concatenate two strings",
    param_descriptions={"a": "First string", "b": "Second string"},
    required_parameters=["a", "b"]
)
def concat(a: str, b: str) -> str:
    return a + b

# Test cases
def test_tool_wrapper_creation():
    """Test that the tool wrapper creates correct schema"""
    assert hasattr(add, "output")
    assert add.output["function"]["name"] == "add"
    assert add.output["function"]["parameters"]["properties"]["a"]["type"] == "integer"
    assert add.output["function"]["parameters"]["properties"]["b"]["type"] == "integer"

def test_create_tools_schema():
    """Test creating tools schema from wrapped functions"""
    tools = [add, concat]
    schema = create_tools_schema(tools)
    assert len(schema) == 2
    assert schema[0]["function"]["name"] == "add"
    assert schema[1]["function"]["name"] == "concat"

def test_create_tools_lookup():
    """Test creating tools lookup dictionary"""
    tools = [add, concat]
    lookup = create_tools_lookup(tools)
    assert "add" in lookup
    assert "concat" in lookup
    assert lookup["add"].funct == add.funct

def test_execute_function():
    """Test executing a function through the wrapper"""
    result = execute_function(
        type("MockCall", (), {
            "function": type("MockFunction", (), {
                "name": "add",
                "arguments": json.dumps({"a": 2, "b": 3})
            })
        }),
        {"add": add}
    )
    assert result == 5

def test_tool_manager_execution():
    """Test ToolManager execution flow"""
    def store_result(result: Dict[str, Any]):
        store_result.last_result = result
    
    manager = ToolManager([add, concat], store_result)
    
    mock_calls = [
        type("MockCall", (), {
            "id": "call1",
            "function": type("MockFunction", (), {
                "name": "add",
                "arguments": json.dumps({"a": 5, "b": 10})
            })
        }),
        type("MockCall", (), {
            "id": "call2",
            "function": type("MockFunction", (), {
                "name": "concat",
                "arguments": json.dumps({"a": "hello", "b": " world"})
            })
        })
    ]
    
    manager.execute_responses(mock_calls)
    assert store_result.last_result["content"] == "hello world"

def test_library_tool_calling(openai_client):
    """Test tool calling through the library abstraction"""
    context = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 123 plus 456?"}
    ]
    
    response = openai_client.create_tool_completion(
        model_name="gpt-4",
        context=context,
        tools=create_tools_schema([add])
    )
    
    assert len(response.tool_calls) > 0
    call = response.tool_calls[0]
    assert call.function.name == "add"
    
    args = json.loads(call.function.arguments)
    assert args["a"] == 123
    assert args["b"] == 456

def test_raw_api_tool_calling(raw_openai_client):
    """Test tool calling through raw API calls"""
    response = raw_openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "What is 789 plus 321?"}],
        tools=[{
            "type": "function",
            "function": {
                "name": "add",
                "description": "Add two numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"}
                    },
                    "required": ["a", "b"]
                }
            }
        }]
    )
    
    message = response.choices[0].message
    assert len(message.tool_calls) > 0
    call = message.tool_calls[0]
    assert call.function.name == "add"
    
    args = json.loads(call.function.arguments)
    assert args["a"] == 789
    assert args["b"] == 321

def test_end_to_end_workflow(openai_client):
    """Test complete workflow from prompt to tool execution"""
    # Initialize context
    context = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "First add 100 and 200, then concatenate 'foo' and 'bar'"}
    ]
    
    # First tool call - addition
    response = openai_client.create_tool_completion(
        model_name="gpt-4",
        context=context,
        tools=create_tools_schema([add, concat])
    )
    
    # Execute first tool
    tool_lookup = create_tools_lookup([add, concat])
    for call in response.tool_calls:
        result = execute_function(call, tool_lookup)
        context.append({
            "role": "tool",
            "tool_call_id": call.id,
            "name": call.function.name,
            "content": str(result)
        })
    
    # Second tool call - concatenation
    response = openai_client.create_tool_completion(
        model_name="gpt-4",
        context=context,
        tools=create_tools_schema([add, concat])
    )
    
    # Execute second tool
    for call in response.tool_calls:
        result = execute_function(call, tool_lookup)
        context.append({
            "role": "tool",
            "tool_call_id": call.id,
            "name": call.function.name,
            "content": str(result)
        })
    
    # Final response
    final_response = openai_client.create_completion(
        model_name="gpt-4",
        context=context
    )
    
    assert "300" in final_response.content
    assert "foobar" in final_response.content
