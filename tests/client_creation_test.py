import pytest
from src.framework.clients import ClientAnthropic
from src.framework.clients import ClientOpenAI

PROJECT_ID = "test-project"
GEMINI_LOCATION = "australia-southeast1"
TEST_KEY = "test-key"

def test_create_openai_client():
    try:
        client = ClientOpenAI.create_openai(TEST_KEY)
        assert client is not None
    except Exception as e:
        pytest.fail(f"Failed to create OpenAI client: {e}")

def test_create_gemini_client():
    try:
        client = ClientOpenAI.create_gemini(PROJECT_ID, GEMINI_LOCATION)
        assert client is not None
    except Exception as e:
        pytest.fail(f"Failed to create Gemini client: {e}")

def test_create_openrouter_client():
    try:
        client = ClientOpenAI.create_openrouter(TEST_KEY)
        assert client is not None
    except Exception as e:
        pytest.fail(f"Failed to create OpenRouter client: {e}")

def test_create_anthropic_client():
    try:
        client = ClientAnthropic(TEST_KEY)
        assert client is not None
    except Exception as e:
        pytest.fail(f"Failed to create Anthropic client: {e}")