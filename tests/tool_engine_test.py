import pytest
from unittest.mock import Mock, MagicMock
from src.core.engine import ToolEngine
from src.clients.response import ResponseWrapperOpenAI
from tests.testing_utils import read_openai_response

# Test response files
GENERIC_RESPONSE_FILE = "tests/test_responses_objects/openai_response_generic.json"
TOOL_RESPONSE_FILE = "tests/test_responses_objects/openai_response_tool_call.json"

from src.tool_calling.tool_calling import openai_function_wrapper

@openai_function_wrapper(
    function_description="Get the current weather in a city",
    parameter_descriptions={"city": "The city to get weather for"}
)
def get_weather(city: str) -> str:
    """Mock weather function that matches the tool call response"""
    return f"Weather in {city}: Sunny, 72°F"

@pytest.fixture
def mock_response_generic():
    """Fixture to load a generic OpenAI response"""
    return ResponseWrapperOpenAI(read_openai_response(GENERIC_RESPONSE_FILE))

@pytest.fixture
def mock_response_tool():
    """Fixture to load an OpenAI response with tool calls"""
    return ResponseWrapperOpenAI(read_openai_response(TOOL_RESPONSE_FILE))

@pytest.fixture
def mock_client():
    """Fixture to create a mock OpenAI client"""
    client = Mock()
    client.create_tool_completion = MagicMock()
    return client

@pytest.fixture
def tool_engine(mock_client):
    """Fixture to create a ToolEngine instance with a mock client"""
    return ToolEngine(
        client=mock_client,
        model_name="gpt-4",
        system_prompt="You are a helpful assistant.",
        tools=[get_weather]
    )

def test_tool_engine_initialization(tool_engine):
    """Test ToolEngine initialization"""
    assert tool_engine.model_name == "gpt-4"
    assert tool_engine.store.system_prompt == "You are a helpful assistant."
    assert len(tool_engine.tools) == 1
    assert tool_engine.tools[0] == get_weather
    assert tool_engine.instructions == []
    assert tool_engine.tasks == []

def test_add_tool(tool_engine):
    """Test adding a new tool"""
    def new_tool(): pass
    tool_engine.add_tool(new_tool)
    assert len(tool_engine.tools) == 2
    assert tool_engine.tools[-1] == new_tool

def test_add_instruction(tool_engine):
    """Test adding an instruction"""
    instruction = "Get the weather in San Francisco"
    tool_engine.add_instruction(instruction)
    assert len(tool_engine.instructions) == 1
    assert tool_engine.instructions[0] == instruction

def test_set_system_prompt(tool_engine):
    """Test setting system prompt"""
    new_prompt = "New system prompt"
    tool_engine.set_system_prompt(new_prompt)
    assert tool_engine.store.system_prompt == new_prompt

def test_execute_regular_response(tool_engine, mock_response_generic):
    """Test executing an instruction that results in a regular response"""
    # Setup mock client to return regular response
    tool_engine.client.create_tool_completion.return_value = mock_response_generic
    
    # Add and execute instruction
    tool_engine.add_instruction("Tell me about black moon")
    tool_engine.run()
    
    # Verify client was called correctly
    tool_engine.client.create_tool_completion.assert_called_once()
    
    # Verify response was stored correctly
    assert len(tool_engine.store.chat_history) == 2
    assert tool_engine.store.chat_history[1]["content"] == mock_response_generic.content

def test_execute_tool_response(tool_engine, mock_response_tool):
    """Test executing an instruction that results in a tool call"""
    # Setup mock client to return tool response
    tool_engine.client.create_tool_completion.return_value = mock_response_tool
    
    # Add and execute instruction
    tool_engine.add_instruction("What's the weather in San Francisco?")
    tool_engine.run()
    
    # Verify client was called correctly
    tool_engine.client.create_tool_completion.assert_called_once()
    
    # Verify tool response was stored
    assert len(tool_engine.store.chat_history) == 3  # Tool call + result
    assert tool_engine.store.chat_history[1] == mock_response_tool.full.choices[0].message
    # Verify function call result was stored
    result = tool_engine.store.chat_history[2]
    assert result["role"] == "tool"
    assert result["name"] == "get_weather"
    assert "Weather in San Francisco" in result["content"]

def test_execute_instructions(tool_engine, mock_response_tool):
    """Test executing multiple instructions"""
    # Setup mock client to return tool response
    tool_engine.client.create_tool_completion.return_value = mock_response_tool
    
    # Execute multiple instructions
    instructions = [
        "What's the weather like?",
        "How's the temperature?"
    ]
    tool_engine.execute_instructions(instructions)
    
    # Verify client was called twice (once for each instruction)
    assert tool_engine.client.create_tool_completion.call_count == 2
    
    # Verify instructions were processed (instructions list should be empty after processing)
    assert len(tool_engine.instructions) == 0
    
    # Verify responses were stored
    assert len(tool_engine.store.chat_history) > 0

def test_complex_interaction(tool_engine, mock_response_generic, mock_response_tool):
    """Test a complex interaction with both regular and tool responses"""
    # Setup mock client to return different responses
    tool_engine.client.create_tool_completion.side_effect = [
        mock_response_generic,  # First call returns regular response
        mock_response_tool      # Second call returns tool response
    ]
    
    # Add multiple instructions
    tool_engine.add_instruction("Tell me about black moon")
    tool_engine.add_instruction("What's the weather in San Francisco?")
    
    # Run the engine
    tool_engine.run()
    
    # Verify client was called twice
    assert tool_engine.client.create_tool_completion.call_count == 2
    
    # Verify responses were stored correctly
    history = tool_engine.store.chat_history
    assert len(history) == 5  # Regular response + tool call + tool result
    assert history[1]["content"] == mock_response_generic.content  # Regular response
    assert history[3] == mock_response_tool.full.choices[0].message  # Tool call
    assert history[4]["role"] == "tool"  # Tool result
