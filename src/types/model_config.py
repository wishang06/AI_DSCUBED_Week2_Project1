from pydantic import BaseModel, ConfigDict
from src.clients.openai_client import ClientOpenAI
from typing import Union

class LLMInit(BaseModel):
    """
    Client + model name configuration for the LLM.

    Attributes:
        client: Union[ClientOpenAI, ClientAnthropic]
        model_name: str
    """
    client: ClientOpenAI
    model_name: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


