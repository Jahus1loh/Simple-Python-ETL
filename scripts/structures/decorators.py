from typing import Callable, Any


def run_once(f: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not wrapper.has_run:  # type: ignore
            wrapper.has_run = True  # type: ignore
            return f(*args, **kwargs)
    wrapper.has_run = False  # type: ignore
    return wrapper
