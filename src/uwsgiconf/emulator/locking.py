
__LOCKS: set[int] = set()


def do_lock(lock_num: int):
    __LOCKS.add(lock_num)


def check_locked(lock_num: int) -> bool:
    return lock_num in __LOCKS


def do_unlock(lock_num: int):
    __LOCKS.discard(lock_num)
