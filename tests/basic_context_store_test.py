import pytest
from src.framework.core.store import BasicChatContextStore
from src.framework.clients.response import ResponseWrapperOpenAI
from tests.testing_utils import read_openai_response

# Assuming these files exist based on your provided structure
RESPONSE_FILE = "tests/test_responses_objects/openai_response_generic.json"

@pytest.fixture
def mock_response_generic():
    """Fixture to load a generic OpenAI response from a JSON file."""
    try:
        return ResponseWrapperOpenAI(read_openai_response(RESPONSE_FILE))
    except Exception as e:  # Catch potential file reading or validation errors
        pytest.fail(f"Failed to load OpenAI response: {e}")

def test_basic_context_store(mock_response_generic):
    store = BasicChatContextStore()
    assert store.system_prompt == ""
    store.set_system_prompt("test")
    assert store.system_prompt == "test"
    store.store_response(mock_response_generic, "user")
    assert store.chat_history == [{"role": "user", "content": mock_response_generic.content}]
    assert store.response_log == [mock_response_generic]
    store.clear()
    assert store.chat_history == []
    store.store_string("test", "user")
    assert store.chat_history == [{"role": "user", "content": "test"}]
    assert store.response_log == [["user", "test"]]
    store.store_response(mock_response_generic, "assistant")
    store.set_system_prompt("system")
    assert store.retrieve() == [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "test"},
        {"role": "assistant", "content": mock_response_generic.content}
    ]