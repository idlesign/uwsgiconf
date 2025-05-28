from typing import Callable, Dict, Optional, Tuple

__RPCS: Dict[str, Callable] = {}


def register(*, name: str, func: Callable):
    __RPCS[name] = func
    return True


def do_call(*args: bytes, name: bytes) -> Optional[bytes]:
    __RPCS[name.decode()](*args)


def get_list() -> Tuple[bytes, ...]:
    return tuple(key.encode() for key in __RPCS)
