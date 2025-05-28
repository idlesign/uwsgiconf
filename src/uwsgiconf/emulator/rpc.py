from collections.abc import Callable

__RPCS: dict[str, Callable] = {}


def register(*, name: str, func: Callable):
    __RPCS[name] = func
    return True


def do_call(*args: bytes, name: bytes) -> bytes | None:
    __RPCS[name.decode()](*args)


def get_list() -> tuple[bytes, ...]:
    return tuple(key.encode() for key in __RPCS)
