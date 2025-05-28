from collections import defaultdict

__CACHES: dict[str, dict[str, bytes | int]] = defaultdict(dict)


def clear(*, cache: str):
    __CACHES[cache].clear()


def set_value(*, key: str, value: bytes, expires: int | None = None, cache: str | None = None):
    __CACHES[cache][key] = value


def do_inc(*, key: str, value: int, expires: int | None = None, cache: str | None = None):
    current = __CACHES[cache].get(key, 0)
    __CACHES[cache][key] = current + value


def do_dec(*, key: str, value: int, expires: int | None = None, cache: str | None = None):
    current = __CACHES[cache].get(key, 0)
    __CACHES[cache][key] = current - value


def do_mul(*, key: str, value: int, expires: int | None = None, cache: str | None = None):
    current = __CACHES[cache].get(key, 0)
    __CACHES[cache][key] = current * value


def do_div(*, key: str, value: int, expires: int | None = None, cache: str | None = None):
    current = __CACHES[cache].get(key, 0)
    __CACHES[cache][key] = current // value


def do_delete(*, key: str, cache: str | None = None) -> bool:
    try:
        del __CACHES[cache][key]
        return True

    except KeyError:
        return False


def get_keys(*, cache: str) -> list[str]:
    return list(__CACHES[cache].keys())


def get_value(*, key: str, cache: str | None = None) -> bytes | int | None:
    return __CACHES[cache].get(key)


def has_key(*, key: str, cache: str | None = None) -> bool:
    return key in __CACHES[cache]

