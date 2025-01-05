import vertexai
import openai
import logging
from google.auth import default
from google.auth.transport import requests as transport_requests
from .response import ResponseWrapperOpenAI

class ClientOpenAI:
    def __init__(self, client):
        # Store the client as an instance attribute
        self.client = client
        # logfire.instrument_openai(self.client)

    @classmethod
    def create_gemini(cls, project, location):
        # Initialize Vertex AI
        vertexai.init(project=project, location=location)

        # Obtain credentials
        credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_request = transport_requests.Request()
        credentials.refresh(auth_request)

        # Initialize OpenAI client
        base_url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/endpoints/openapi"
        client = openai.OpenAI(
            base_url=base_url,
            api_key=credentials.token  # Use the refreshed token
        )

        # Return an instance of OpenAIWrapper with the initialized client
        return cls(client)
    
    @classmethod
    def create_openai(cls, api_key):
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        return cls(client)

    @classmethod
    def create_openrouter(cls, api_key):
        # Initialize OpenAI client
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        return cls(client)

    def create_completion(self, model_name, context):
        response = self.client.chat.completions.create(model=model_name, 
                                                   messages=context,
                                                   temperature=1,
                                                   max_tokens=8000,
                                                   top_p=1)
        return ResponseWrapperOpenAI(response)
    
    def create_tool_completion(self, model_name, context, tools):
        response = self.client.chat.completions.create(model=model_name, 
                                                   messages=context,
                                                   temperature=1,
                                                   max_tokens=8000,
                                                   top_p=1,
                                                   tools=tools,
                                                   tool_choice=None,
                                                   parallel_tool_calls=False
                                                   )
        return ResponseWrapperOpenAI(response)

