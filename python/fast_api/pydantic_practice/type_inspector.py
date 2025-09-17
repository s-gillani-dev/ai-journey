from typing import get_type_hints, get_origin, get_args, List, Dict, Optional
from functools import wraps

def log_type_hints(func):
    """
    Decorator that inspects and logs type hints of the target function.
    It also shows the origin and arguments of generic types.
    """
    hints = get_type_hints(func)
    print(f"\nType hints for {func.__name__}: {hints}")

    for param, hint in hints.items():
        origin = get_origin(hint)
        args = get_args(hint)
        if origin:
            print(f" - {param}: origin={origin}, args={args}")
        else:
            print(f" - {param}: (simple type)")

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    
    return wrapper
