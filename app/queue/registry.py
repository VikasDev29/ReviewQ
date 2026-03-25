from typing import Callable, Awaitable, Any

_registry: dict[str, Callable[..., Awaitable[Any]]] = {}

def register_task(name: str):
    def decorator(fn: Callable):
        _registry[name] = fn
        return fn
    return decorator

def get_task(name: str) -> Callable | None:
    return _registry.get(name)