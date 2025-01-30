from enum import Enum, auto


class EngineObserverEventType(Enum):
    RESPONSE = auto()
    FUNCTION_CALL = auto()
    FUNCTION_RESULT = auto()
    STATUS_UPDATE = auto()
    GET_INPUT = auto()
    GET_CONFIRMATION = auto()
    STREAM = auto()
    AWAITING_STREAM_COMPLETION = auto()
