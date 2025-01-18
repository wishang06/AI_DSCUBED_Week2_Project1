from src.framework.clients import ClientAnthropic
from src.framework.clients import ClientOpenAI
from src.framework.clients.response import ResponseWrapper
import dotenv
import os
import pprint

dotenv.load_dotenv()

MODEL_NAME_OPENAI = "gpt-4o-mini"
MODEL_NAME_GEMINI = "google/gemini-1.5-pro-002"
MODEL_NAME_ANTHROPIC = "claude-3-5-haiku-latest"
MODEL_NAME_OPENROUTER = "meta-llama/llama-3.3-70b-instruct"
TEST_CONTEXT = [{"role": "user", "content": "Does the black moon howl?"}]

def test_openai_response():
    openai_client = ClientOpenAI.create_openai(os.getenv("OPENAI_API_KEY"))
    openai_response_generic = openai_client.create_completion(MODEL_NAME_OPENAI, context=TEST_CONTEXT)

    print(f"\nOpenAI response for model '{MODEL_NAME_OPENAI}':")
    pprint.pprint(openai_response_generic)

    assert openai_response_generic is not None
    assert isinstance(openai_response_generic, ResponseWrapper)

def test_gemini_response():
    openai_client = ClientOpenAI.create_gemini(os.getenv("GOOGLE_CLOUD_PROJECT"), os.getenv("GOOGLE_CLOUD_LOCATION"))
    gemini_response_generic = openai_client.create_completion(MODEL_NAME_GEMINI, context=TEST_CONTEXT)
    
    print(f"\nGemini response for model '{MODEL_NAME_GEMINI}':")
    pprint.pprint(gemini_response_generic)
    
    assert gemini_response_generic is not None
    assert isinstance(gemini_response_generic, ResponseWrapper)

def test_openrouter_response():
    openai_client = ClientOpenAI.create_openrouter(os.getenv("OPENROUTER_API_KEY"))
    openrouter_response_generic = openai_client.create_completion(MODEL_NAME_OPENROUTER, context=TEST_CONTEXT)
    
    print(f"\nOpenRouter response for model '{MODEL_NAME_OPENROUTER}':")
    pprint.pprint(openrouter_response_generic)
    
    assert openrouter_response_generic is not None
    assert isinstance(openrouter_response_generic, ResponseWrapper)

def test_anthropic_response():
    anthropic_client = ClientAnthropic(os.getenv("ANTHROPIC_API_KEY"))
    anthropic_response_generic = anthropic_client.create_completion(MODEL_NAME_ANTHROPIC, context=TEST_CONTEXT)
    
    print(f"\nAnthropic response for model '{MODEL_NAME_ANTHROPIC}':")
    pprint.pprint(anthropic_response_generic)
    
    assert anthropic_response_generic is not None
    assert isinstance(anthropic_response_generic, ResponseWrapper)