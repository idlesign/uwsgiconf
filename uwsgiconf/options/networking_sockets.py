from ..base import ParametrizedValue
from ..utils import listify


if False:  # pragma: nocover
    from .routing_modifiers import Modifier


class Socket(ParametrizedValue):

    opt_key = ''
    args_joiner = ','

    def __init__(self, address, bound_workers=None, modifier=None):
        """
        :param str|unicode|SocketShared address: Address ([host]:port or socket file) to bind socket to.

        :param  str|unicode|int|list bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param Modifier modifier: Socket routing modifier.

        """
        self.address = address
        self.bound_workers = listify(bound_workers or [])

        self._make_section_like()

        if modifier:
            self._set('%s-modifier1' % self.name, modifier.code)

            submod = modifier.submod

            if submod:
                self._set('%s-modifier2' % self.name, modifier.submod)

        super(Socket, self).__init__()

    def __str__(self):
        if self.address not in self.args:
            self.args.insert(0, self.address)

        result = super(Socket, self).__str__()

        self.args.pop(0)

        return result


class SocketDefault(Socket):
    """Bind using default protocol. See ``default_socket_type`` option."""

    name = 'socket'


class SocketHttp(Socket):
    """Bind to the specified socket using HTTP"""

    name = 'http-socket'

    def __init__(self, address, http11=False, bound_workers=None, modifier=None):
        """
        :param str|unicode|SocketShared address: Address ([host]:port or socket file) to bind socket to.

        :param bool http11: Keep-Alive support. If set the server will try to maintain
            the connection opened if a bunch of rules are respected.

            This is not a smart http 1.1 parser (to avoid parsing the whole response)
            but assumes the developer is generating the right headers.

            This has been added to support RTSP protocol for video streaming.

        :param  str|unicode|int|list bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param Modifier modifier: Socket routing modifier.

        """
        if http11:
            self.name = 'http11-socket'

        super(SocketHttp, self).__init__(address, bound_workers=bound_workers, modifier=modifier)


class SocketHttps(Socket):
    """Bind to the specified socket using HTTPS"""

    name = 'https-socket'

    def __init__(self, address, cert, key, ciphers=None, client_ca=None, bound_workers=None, modifier=None):
        """
        :param str|unicode|SocketShared address: Address ([host]:port or socket file) to bind socket to.

        :param str|unicode cert: Certificate file.

        :param str|unicode key: Private key file.

        :param str|unicode ciphers: Ciphers [alias] string.

            Example:
                * DEFAULT
                * HIGH
                * DHE, EDH

            * https://www.openssl.org/docs/man1.1.0/apps/ciphers.html

        :param str|unicode client_ca: Client CA file for client-based auth.

            .. note: You can prepend ! (exclamation mark) to make client certificate
                authentication mandatory.

        :param  str|unicode|int|list bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param Modifier modifier: Socket routing modifier.
        """
        super(SocketHttps, self).__init__(address, bound_workers=bound_workers, modifier=modifier)
        args = [cert, key]

        if ciphers or client_ca:
            args.extend([ciphers or '', client_ca or ''])

        self.args.extend(args)


class SocketUwsgi(Socket):
    """uwSGI specific socket using ``uwsgi`` protocol."""

    name = 'uwsgi-socket'

    def __init__(self, address, persistent=False, bound_workers=None, modifier=None):
        """
        :param str|unicode|SocketShared address: Address ([host]:port or socket file) to bind socket to.

        :param bool persistent: Use persistent uwsgi protocol (puwsgi).

        :param  str|unicode|int|list bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param Modifier modifier: Socket routing modifier.

        """
        if persistent:
            self.name = 'puwsgi-socket'

        super(SocketUwsgi, self).__init__(address, bound_workers=bound_workers, modifier=modifier)


class SocketUwsgis(SocketHttps):
    """uwSGI specific socket using ``uwsgi`` protocol over SSL."""

    name = 'suwsgi-socket'


class SocketUdp(Socket):
    """Run the udp server on the specified address.

    .. note:: Mainly useful for SNMP or shared UDP logging.

    """
    name = 'udp'


class SocketFastcgi(Socket):
    """Bind to the specified socket using FastCGI."""

    name = 'fastcgi-socket'

    def __init__(self, address, nph=False, bound_workers=None, modifier=None):
        """
        :param str|unicode|SocketShared address: Address ([host]:port or socket file) to bind socket to.

        :param bool nph: Use NPH mode ("no-parsed-header" - bypass the server completely by sending
            the complete HTTP header directly to the browser).

        :param  str|unicode|int|list bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param Modifier modifier: Socket routing modifier.

        """
        if nph:
            self.name = 'fastcgi-nph-socket'

        super(SocketFastcgi, self).__init__(address, bound_workers=bound_workers, modifier=modifier)


class SocketScgi(Socket):
    """Bind to the specified UNIX/TCP socket using SCGI protocol."""

    name = 'scgi-socket'

    def __init__(self, address, nph=False, bound_workers=None, modifier=None):
        """
        :param str|unicode|SocketShared address: Address ([host]:port or socket file) to bind socket to.

        :param bool nph: Use NPH mode ("no-parsed-header" - bypass the server completely by sending
            the complete HTTP header directly to the browser).

        :param  str|unicode|int|list bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param Modifier modifier: Socket routing modifier.

        """
        if nph:
            self.name = 'scgi-nph-socket'

        super(SocketScgi, self).__init__(address, bound_workers=bound_workers, modifier=modifier)


class SocketRaw(Socket):
    """Bind to the specified UNIX/TCP socket using RAW protocol.

    Raw mode allows you to directly parse the request in your application callable.
    Instead of getting a list of CGI vars/headers in your callable you only get
    the file descriptor soon after accept().

    You can then read()/write() to that file descriptor in full freedom.

    .. note:: Raw mode disables request logging.

    .. warning:: Use it as a low-level socket wrapper.

    """
    name = 'raw-socket'


class SocketShared(Socket):
    """Create a shared socket for advanced jailing or IPC purposes.

    Allows you to create a socket early in the server's startup
    and use it after privileges drop or jailing. This can be used
    to bind to privileged (<1024) ports.

    Shared sockets are a way to share sockets among various uWSGI components:
    you can use that to share a socket between the fastrouter and uWSGI instance.

    """
    name = 'shared-socket'

    def __init__(self, address, undeferred=False, bound_workers=None, modifier=None):
        """
        :param str|unicode address: Address ([host]:port or socket file) to bind socket to.

        :param bool undeferred: Use shared socket undeferred mode.

        :param  str|unicode|int|list bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param Modifier modifier: Socket routing modifier.

        """
        if undeferred:
            self.name = 'undeferred-shared-socket'

        super(SocketShared, self).__init__(address, bound_workers=bound_workers, modifier=modifier)


class SocketZeromq(Socket):
    """Introduce zeromq pub/sub pair."""

    name = 'zeromq-socket'
