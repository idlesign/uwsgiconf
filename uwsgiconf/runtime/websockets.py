from .. import uwsgi


handshake = uwsgi.websocket_handshake


def recv(request_context=None, non_blocking=False):
    """Receives data from websocket.

    :param request_context:

    :param bool non_blocking:

    :rtype: bytes|str

    :raises IOError: If unable to receive a message.
    """

    if non_blocking:
        result = uwsgi.websocket_recv_nb(request_context)

    else:
        result = uwsgi.websocket_recv(request_context)

    return result


def send(message, request_context=None, binary=False):
    """Sends a message to websocket.

    :param str message: data to send

    :param request_context:

    :raises IOError: If unable to send a message.
    """
    if binary:
        return uwsgi.websocket_send_binary(message, request_context)

    return uwsgi.websocket_send(message, request_context)
