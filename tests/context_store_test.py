import pytest
from src.core.store import ContextStore
from src.clients.response import ResponseWrapperOpenAI
from tests.testing_utils import read_openai_response

# Test response files
GENERIC_RESPONSE_FILE = "tests/test_responses_objects/openai_response_generic.json"
TOOL_RESPONSE_FILE = "tests/test_responses_objects/openai_response_tool_call.json"

@pytest.fixture
def mock_response_generic():
    """Fixture to load a generic OpenAI response from a JSON file."""
    try:
        return ResponseWrapperOpenAI(read_openai_response(GENERIC_RESPONSE_FILE))
    except Exception as e:  # Catch potential file reading or validation errors
        pytest.fail(f"Failed to load OpenAI response: {e}")

@pytest.fixture
def mock_response_tool():
    """Fixture to load an OpenAI response with tool calls from a JSON file."""
    try:
        return ResponseWrapperOpenAI(read_openai_response(TOOL_RESPONSE_FILE))
    except Exception as e:  # Catch potential file reading or validation errors
        pytest.fail(f"Failed to load OpenAI tool response: {e}")

def test_context_store_initialization():
    # Test default initialization
    store = ContextStore()
    assert store.system_prompt == ""
    assert store.response_log == []
    assert store.chat_history == []

    # Test initialization with system prompt
    store = ContextStore(system_prompt="test system")
    assert store.system_prompt == "test system"
    assert store.response_log == []
    assert store.chat_history == []

def test_context_store_system_prompt():
    store = ContextStore()
    assert store.system_prompt == ""
    store.set_system_prompt("test")
    assert store.system_prompt == "test"

def test_context_store_response(mock_response_generic):
    store = ContextStore()
    store.store_response(mock_response_generic, "user")
    assert store.chat_history == [{"role": "user", "content": mock_response_generic.content}]
    assert store.response_log == [mock_response_generic]

def test_context_store_string():
    store = ContextStore()
    store.store_string("test message", "user")
    assert store.chat_history == [{"role": "user", "content": "test message"}]
    assert store.response_log == [["user", "test message"]]

def test_context_store_tool_response(mock_response_tool):
    store = ContextStore()
    store.store_tool_response(mock_response_tool)
    assert store.chat_history == [mock_response_tool.full.choices[0].message]
    assert store.response_log == [mock_response_tool]

def test_context_store_retrieve():
    store = ContextStore(system_prompt="system message")
    store.store_string("user message", "user")
    store.store_string("assistant message", "assistant")
    
    expected_history = [
        {"role": "system", "content": "system message"},
        {"role": "user", "content": "user message"},
        {"role": "assistant", "content": "assistant message"}
    ]
    assert store.retrieve() == expected_history

def test_context_store_clear():
    store = ContextStore(system_prompt="test system")
    store.store_string("test message", "user")
    
    store.clear()
    assert store.system_prompt == ""
    assert store.response_log == []
    assert store.chat_history == []

def test_context_store_complex_interaction(mock_response_generic, mock_response_tool):
    store = ContextStore()
    
    # Add system prompt
    store.set_system_prompt("system message")
    
    # Store string message
    store.store_string("user message", "user")
    
    # Store response
    store.store_response(mock_response_generic, "assistant")
    
    # Store tool response
    store.store_tool_response(mock_response_tool)
    
    # Verify chat history
    history = store.retrieve()
    assert history[0] == {"role": "system", "content": "system message"}
    assert history[1] == {"role": "user", "content": "user message"}
    assert history[2] == {"role": "assistant", "content": mock_response_generic.content}
    assert history[3] == mock_response_tool.full.choices[0].message
    
    # Verify response log
    assert len(store.response_log) == 3
    assert store.response_log[0] == ["user", "user message"]
    assert store.response_log[1] == mock_response_generic
    assert store.response_log[2] == mock_response_tool
