import asyncio
from typing import Any, Callable, Dict, List, NewType, Union

# TODO use _type


# Type for tool function
ToolFunction = Callable[..., Any]
AsyncToolFunction = Callable[..., "asyncio.Future[Any]"]
AsyncOrSyncToolFunction = Union[ToolFunction, AsyncToolFunction]


ModelFormattedDictTool = NewType("ModelFormattedDictTool", dict[str, Any])
ContextType = NewType("ContextType", List[Dict[str, Any]])

ModelNameStr = NewType("ModelNameStr", str)


SessionID = NewType("SessionID", str)
