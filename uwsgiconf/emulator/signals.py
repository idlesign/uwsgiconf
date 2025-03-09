from dataclasses import dataclass
from typing import Dict, Callable


@dataclass
class SignalInfo:

    num: int
    target: str
    func: Callable
    schedule: str = ''


__SIGNALS: Dict[int, SignalInfo] = {}


def register(*, num: int, target: str, func: Callable):
    __SIGNALS[num] = SignalInfo(num, target, func)


def is_registered(*, num: int) -> int:
    return int(num in __SIGNALS)


def do_signal(*, num: int):
    __SIGNALS[num].func(num)


def cleanup():
    __SIGNALS.clear()
