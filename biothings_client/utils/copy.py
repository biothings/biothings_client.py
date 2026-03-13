import types
from typing import Any, Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def copy_func(f: F, name: Optional[str] = None) -> F:
    """
    return a function with same code, globals, defaults, closure, and
    name (or provide a new name)
    """
    fn = types.FunctionType(f.__code__, f.__globals__, name or f.__name__, f.__defaults__, f.__closure__)
    # in case f was given attrs (note this dict is a shallow copy):
    fn.__dict__.update(f.__dict__)
    return fn  # type: ignore[return-value]
