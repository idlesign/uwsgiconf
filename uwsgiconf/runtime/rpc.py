from .. import uwsgi
from ..utils import encode, decode, get_logger

_LOG = get_logger(__name__)


def register_rpc(name=None):
    """Decorator. Allows registering a function for RPC.

    * http://uwsgi.readthedocs.io/en/latest/RPC.html

    Example:

        .. code-block:: python

            @register_rpc()
            def expose_me():
                do()


    :param str|unicode name: RPC function name to associate
        with decorated function.

    :rtype: callable
    """
    def wrapper(func):
        func_name = func.__name__
        rpc_name = name or func_name

        uwsgi.register_rpc(rpc_name, func)

        _LOG.debug("Registering '%s' for RPC under '%s' alias ...", func_name, rpc_name)

        return func

    return wrapper


def make_rpc_call(func_name, args=None, remote=None):
    """Performs an RPC function call (local or remote) with the given arguments.

    :param str|unicode func_name: RPC function name to call.

    :param Iterable args: Function arguments.

    :param str|unicode remote:

    :rtype: bytes|str

    :raises ValueError: If unable to call RPC function.

    """
    args = args or []
    args = [encode(str(arg)) for arg in args]

    if remote:
        result = uwsgi.rpc(remote, func_name, *args)
    else:
        result = uwsgi.call(func_name, *args)

    return decode(result)


def get_rpc_list():
    """Returns registered RPC functions names.

    :rtype: tuple
    """
    return uwsgi.rpc_list()
