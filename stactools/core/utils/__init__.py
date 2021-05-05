from typing import Callable, Optional, TypeVar

T = TypeVar('T')
U = TypeVar('U')


def map_opt(fn: Callable[[T], U], v: Optional[T]) -> Optional[U]:
    """Maps the value of an option to another value, returning
    None if the input option is None.
    """
    return v if v is None else fn(v)
