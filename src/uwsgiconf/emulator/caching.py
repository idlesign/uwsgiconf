from collections import defaultdict
from typing import Dict, List, Optional, Union

__CACHES: Dict[str, Dict[str, Union[bytes, int]]] = defaultdict(dict)


def clear(*, cache: str):
    __CACHES[cache].clear()


def set_value(*, key: str, value: bytes, expires: int = None, cache: str = None):
    __CACHES[cache][key] = value


def do_inc(*, key: str, value: int, expires: int = None, cache: str = None):
    current = __CACHES[cache].get(key, 0)
    __CACHES[cache][key] = current + value


def do_dec(*, key: str, value: int, expires: int = None, cache: str = None):
    current = __CACHES[cache].get(key, 0)
    __CACHES[cache][key] = current - value


def do_mul(*, key: str, value: int, expires: int = None, cache: str = None):
    current = __CACHES[cache].get(key, 0)
    __CACHES[cache][key] = current * value


def do_div(*, key: str, value: int, expires: int = None, cache: str = None):
    current = __CACHES[cache].get(key, 0)
    __CACHES[cache][key] = current // value


def do_delete(*, key: str, cache: str = None) -> bool:
    try:
        del __CACHES[cache][key]
        return True

    except KeyError:
        return False


def get_keys(*, cache: str) -> List[str]:
    return list(__CACHES[cache].keys())


def get_value(*, key: str, cache: str = None) -> Optional[Union[bytes, int]]:
    return __CACHES[cache].get(key)


def has_key(*, key: str, cache: str = None) -> bool:
    return key in __CACHES[cache]

