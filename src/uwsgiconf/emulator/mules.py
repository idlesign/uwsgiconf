

def send_mule_msg(*, message: str | bytes, mule_farm: str | int | None = None) -> bool:
    from ..runtime.mules import _mule_messages_hook  # noqa: PLC0415
    return _mule_messages_hook(message)


def send_farm_msg(*, farm: str, message: str | bytes) -> bool:
    from ..runtime.mules import _mule_messages_hook  # noqa: PLC0415
    return _mule_messages_hook(message)
