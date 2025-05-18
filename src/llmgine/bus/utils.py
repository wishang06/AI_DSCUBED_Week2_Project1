from typing import Any, Callable

import inspect


def is_async_function(function: Callable[..., Any]) -> bool:
    return inspect.iscoroutinefunction(function)

