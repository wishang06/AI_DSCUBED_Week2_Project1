import pytest
from unittest.mock import MagicMock, patch
from src.core.engine import BasicChatContextEngine
from src.clients.openai_client import ClientOpenAI
from src.clients.anthropic_client import ClientAnthropic
from src.core.store import BasicChatContextStore
from src.clients.response import ResponseWrapperOpenAI

class TestBasicContextEngine:
    @pytest.fixture
    def context_engine(self):
        client = ClientOpenAI.create_openai("api_key")
        model_name = "test_model"
        system_prompt = "You are a helpful assistant."
        return BasicChatContextEngine(client, model_name, system_prompt)

    def test_init(self, context_engine):
        assert isinstance(context_engine.client, ClientOpenAI)
        assert context_engine.model_name == "test_model"
        assert isinstance(context_engine.store, BasicChatContextStore)
        assert context_engine.store.system_prompt == "You are a helpful assistant."

    def test_compile(self, context_engine):
        message = "Hello, how are you?"
        context = context_engine.compile(message)
        assert "user" in context[1]["role"]
        assert context[1]["content"] == "Hello, how are you?"
        assert "system" in context[0]["role"]
        assert context[0]["content"] == "You are a helpful assistant."

    @patch('src.clients.openai_client.ClientOpenAI.create_completion')
    def test_execute(self, mock_create_completion, context_engine):
        from tests.testing_utils import read_openai_response
        openai_response = read_openai_response("tests/test_responses_objects/openai_response_generic.json")
        mock_create_completion.return_value = ResponseWrapperOpenAI(openai_response)

        message = "What is the weather like today?"
        response = context_engine.execute(message)
        assert response.content == "The phrase \"black moon\" can refer to different concepts depending on context, such as a second new moon in a calendar month or a more abstract idea often linked to mythology or literature. As for howling, typically, it's wolves that are known to howl, not moon phases themselves. \n\nIf you're referring to a specific work of fiction, song, or metaphorical expression involving \"black moon\" and \"howl,\" please provide more details, and I'd be happy to help further!"

        chat_history = context_engine.store.retrieve()
        assert "assistant" in chat_history[-1]["role"]
        assert chat_history[-1]["content"] == "The phrase \"black moon\" can refer to different concepts depending on context, such as a second new moon in a calendar month or a more abstract idea often linked to mythology or literature. As for howling, typically, it's wolves that are known to howl, not moon phases themselves. \n\nIf you're referring to a specific work of fiction, song, or metaphorical expression involving \"black moon\" and \"howl,\" please provide more details, and I'd be happy to help further!"
