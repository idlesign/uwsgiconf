from pathlib import Path
from typing import TYPE_CHECKING

from ..base import ParametrizedValue
from ..typehints import Strlist
from ..utils import listify

if TYPE_CHECKING:
    from .routing_modifiers import Modifier


class Socket(ParametrizedValue):

    opt_key = ''
    args_joiner = ','

    def __init__(self, address: 'StrShaSoc', *, bound_workers: Strlist = None, modifier: 'Modifier' = None):
        """
        :param address: Address ([host]:port or socket file) to bind socket to.

        :param  bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param modifier: Socket routing modifier.

        """
        self.address = address
        self.bound_workers = listify(bound_workers or [])

        self._make_section_like()

        if modifier:
            self._set(f'{self.name}-modifier1', modifier.code)

            submod = modifier.submod

            if submod:
                self._set(f'{self.name}-modifier2', modifier.submod)

        super().__init__()

    def __str__(self):
        if self.address not in self.args:
            self.args.insert(0, self.address)

        result = super().__str__()

        self.args.pop(0)

        return result


class SocketShared(Socket):
    """Create a shared socket for advanced jailing or IPC purposes.

    Allows you to create a socket early in the server's startup
    and use it after privileges drop or jailing. This can be used
    to bind to privileged (<1024) ports.

    Shared sockets are a way to share sockets among various uWSGI components:
    you can use that to share a socket between the fastrouter and uWSGI instance.

    """
    name = 'shared-socket'

    def __init__(
            self,
            address: str,
            *,
            undeferred: bool = False,
            bound_workers: Strlist = None,
            modifier: 'Modifier' = None
    ):
        """
        :param address: Address ([host]:port or socket file) to bind socket to.

        :param undeferred: Use shared socket undeferred mode.

        :param bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param Modifier modifier: Socket routing modifier.

        """
        if undeferred:
            self.name = 'undeferred-shared-socket'

        super().__init__(address, bound_workers=bound_workers, modifier=modifier)


StrShaSoc = SocketShared | str


class SocketDefault(Socket):
    """Bind using default protocol. See ``default_socket_type`` option."""

    name = 'socket'


class SocketHttp(Socket):
    """Bind to the specified socket using HTTP"""

    name = 'http-socket'

    def __init__(
            self,
            address: StrShaSoc,
            *,
            http11: bool = False,
            bound_workers: Strlist = None,
            modifier: 'Modifier' = None
    ):
        """
        :param address: Address ([host]:port or socket file) to bind socket to.

        :param http11: Keep-Alive support. If set the server will try to maintain
            the connection opened if a bunch of rules are respected.

            This is not a smart http 1.1 parser (to avoid parsing the whole response)
            but assumes the developer is generating the right headers.

            This has been added to support RTSP protocol for video streaming.

        :param  bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param modifier: Socket routing modifier.

        """
        if http11:
            self.name = 'http11-socket'

        super().__init__(address, bound_workers=bound_workers, modifier=modifier)


class SocketHttps(Socket):
    """Bind to the specified socket using HTTPS"""

    name = 'https-socket'

    def __init__(
            self,
            address: StrShaSoc,
            *,
            cert: str,
            key: str,
            ciphers: str | None = None,
            client_ca: str | None = None,
            bound_workers: Strlist = None,
            modifier: 'Modifier' = None
    ):
        """
        :param address: Address ([host]:port or socket file) to bind socket to.

        :param cert: Certificate file.

        :param key: Private key file.

        :param ciphers: Ciphers [alias] string.

            Example:
                * DEFAULT
                * HIGH
                * DHE, EDH

            * https://www.openssl.org/docs/man1.1.0/apps/ciphers.html

        :param client_ca: Client CA file for client-based auth.

            .. note: You can prepend ! (exclamation mark) to make client certificate
                authentication mandatory.

        :param bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param Modifier modifier: Socket routing modifier.
        """
        super().__init__(address, bound_workers=bound_workers, modifier=modifier)
        args = [cert, key]

        if ciphers or client_ca:
            args.extend([ciphers or '', client_ca or ''])

        self.args.extend(args)

    @classmethod
    def get_certbot_paths(cls, domain: str) -> tuple[str, str]:
        """Returns a tuple of paths for files (certificates_chain, private_key)
        from Certbot https://certbot.eff.org

        Those paths can be used to pass into Socket initializer.

        .. note:: If files not found empty strings are returned.

        :param domain: Domain name to get filepaths for.

        """
        certs_root = Path('/etc/letsencrypt/live/')
        certs_chain = certs_root / domain / 'fullchain.pem'
        certs_private = certs_root / domain / 'privkey.pem'

        if certs_chain.exists() and certs_private.exists():
            return f'{certs_chain}', f'{certs_private}'

        return '', ''


class SocketUwsgi(Socket):
    """uwSGI specific socket using ``uwsgi`` protocol."""

    name = 'uwsgi-socket'

    def __init__(
            self,
            address: StrShaSoc,
            *,
            persistent: bool = False,
            bound_workers: Strlist = None,
            modifier: 'Modifier' = None
    ):
        """
        :param address: Address ([host]:port or socket file) to bind socket to.

        :param persistent: Use persistent uwsgi protocol (puwsgi).

        :param  bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param modifier: Socket routing modifier.

        """
        if persistent:
            self.name = 'puwsgi-socket'

        super().__init__(address, bound_workers=bound_workers, modifier=modifier)


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

    def __init__(
            self,
            address: StrShaSoc,
            *,
            nph: bool = False,
            bound_workers: Strlist = None,
            modifier: 'Modifier' = None
    ):
        """
        :param address: Address ([host]:port or socket file) to bind socket to.

        :param nph: Use NPH mode ("no-parsed-header" - bypass the server completely by sending
            the complete HTTP header directly to the browser).

        :param  bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param modifier: Socket routing modifier.

        """
        if nph:
            self.name = 'fastcgi-nph-socket'

        super().__init__(address, bound_workers=bound_workers, modifier=modifier)


class SocketScgi(Socket):
    """Bind to the specified UNIX/TCP socket using SCGI protocol."""

    name = 'scgi-socket'

    def __init__(
            self,
            address: StrShaSoc,
            *,
            nph: bool = False,
            bound_workers: Strlist = None,
            modifier: 'Modifier' = None
    ):
        """
        :param address: Address ([host]:port or socket file) to bind socket to.

        :param nph: Use NPH mode ("no-parsed-header" - bypass the server completely by sending
            the complete HTTP header directly to the browser).

        :param  bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        :param modifier: Socket routing modifier.

        """
        if nph:
            self.name = 'scgi-nph-socket'

        super().__init__(address, bound_workers=bound_workers, modifier=modifier)


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


class SocketZeromq(Socket):
    """Introduce zeromq pub/sub pair."""

    name = 'zeromq-socket'
