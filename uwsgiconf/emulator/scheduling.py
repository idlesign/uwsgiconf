from .signals import __SIGNALS


def add_timer(*, signum: int, period: int):
    __SIGNALS[signum].schedule = f'timer: {period=}'


def add_ms_timer(*, signum: int, period: int):
    __SIGNALS[signum].schedule = f'timer-ms: {period=}'


def add_rb_timer(*, signum: int, period: int, repeat: int = 0):
    __SIGNALS[signum].schedule = f'timer-rb: {period=} {repeat=}'
