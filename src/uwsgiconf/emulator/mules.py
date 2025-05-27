from typing import Union


def send_mule_msg(*, message: Union[str, bytes], mule_farm: Union[str, int] = None) -> bool:
    from ..runtime.mules import _mule_messages_hook
    return _mule_messages_hook(message)


def send_farm_msg(*, farm: str, message: Union[str, bytes]) -> bool:
    from ..runtime.mules import _mule_messages_hook
    return _mule_messages_hook(message)
