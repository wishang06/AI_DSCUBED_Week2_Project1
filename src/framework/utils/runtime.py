from pydantic import BaseModel
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Union
from src.framework.clients.openai_client import ClientOpenAI
from src.framework.clients.openrouter_client import ClientOpenRouter


@dataclass
class Runtime:
    session_id: str = datetime.now().strftime("%Y%m%d%H%M%S")
    client_list: Optional[List[Union[ClientOpenAI, ClientOpenRouter]]] = field(default_factory=list)

global_runtime = None

def init_global_runtime():
    global global_runtime
    global_runtime = Runtime()

def get_global_runtime():
    global global_runtime
    return global_runtime
