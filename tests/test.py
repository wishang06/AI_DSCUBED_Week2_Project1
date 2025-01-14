from typing import TypeVar, Callable

T = TypeVar('T')

def typed_wrapper(
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any
) -> T:
    return func(*args, **kwargs)