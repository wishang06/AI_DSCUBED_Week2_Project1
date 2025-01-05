from pydantic import BaseModel
from src.clients.anthropic_client import ClientAnthropic
from src.clients.openai_client import ClientOpenAI
from typing import Union

class LLMInit(BaseModel):
    """
    Client + model name configuration for the LLM.

    Attributes:
        client: Union[ClientOpenAI, ClientAnthropic]
        model_name: str
    """
    client: Union[ClientOpenAI, ClientAnthropic]
    model_name: str