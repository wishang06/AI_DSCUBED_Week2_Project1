import pytest
from src.framework.clients.response import ResponseWrapperOpenAI
from tests.testing_utils import read_openai_response, read_anthropic_response

# Assuming these files exist based on your provided structure
OPENAI_RESPONSE_FILE = "tests/test_responses_objects/openai_response_generic.json"
ANTHROPIC_RESPONSE_FILE = "tests/test_responses_objects/anthropic_response_generic.json"

@pytest.fixture
def mock_openai_response_generic():
    """Fixture to load a generic OpenAI response from a JSON file."""
    try:
        return read_openai_response(OPENAI_RESPONSE_FILE)
    except Exception as e:  # Catch potential file reading or validation errors
        pytest.fail(f"Failed to load OpenAI response: {e}")

@pytest.fixture
def mock_anthropic_response_generic():
    """Fixture to load a generic Anthropic response from a JSON file."""
    try:
        return read_anthropic_response(ANTHROPIC_RESPONSE_FILE)
    except Exception as e:
        pytest.fail(f"Failed to load Anthropic response: {e}")

def test_response_wrapper_openai(mock_openai_response_generic):
    """Test parsing an OpenAI response into a ResponseObject."""
    response = ResponseWrapperOpenAI(mock_openai_response_generic)
    
    assert response is not None
    assert isinstance(response, ResponseWrapperOpenAI)
    assert response.full == mock_openai_response_generic
    assert response.content == mock_openai_response_generic.choices[0].message.content
    assert response.tokens_input == mock_openai_response_generic.usage.prompt_tokens
    assert response.tokens_output == mock_openai_response_generic.usage.completion_tokens
    assert response.to_json == mock_openai_response_generic.to_json()

# def test_response_wrapper_anthropic(mock_anthropic_response_generic):
#     """Test parsing an Anthropic response into a ResponseObject."""
#     response = ResponseWrapperAnthropic(mock_anthropic_response_generic)
    
#     assert response is not None
#     assert isinstance(response, ResponseWrapperAnthropic)
#     assert response.full == mock_anthropic_response_generic
#     assert response.content == mock_anthropic_response_generic.content[0].text
#     assert response.function_calls == None  # To do
#     assert response.tokens_input == mock_anthropic_response_generic.usage.input_tokens
#     assert response.tokens_output == mock_anthropic_response_generic.usage.output_tokens
#     assert response.to_json == mock_anthropic_response_generic.to_json()