from pydantic import BaseModel, ConfigDict
from src.framework.clients import ClientOpenAI


class LLMInit(BaseModel):
    """
    Client + model name configuration for the LLM.

    Attributes:
        client: Union[ClientOpenAI]
        model_name: str
    """
    client: ClientOpenAI
    model_name: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


