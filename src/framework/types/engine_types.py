from pydantic import BaseModel
from typing import Literal

class ToolEngineModes(BaseModel):
    """
    Tool Engine Modes
    """
    mode: Literal["silent", "normal", "continuous"]

