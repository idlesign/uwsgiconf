from os import geteuid
from urllib.parse import parse_qs, urlsplit

from ..base import OptionsGroup
from ..exceptions import ConfigurationError
from ..typehints import Intlist, Strbool
from ..utils import listify
from .networking_sockets import *


class Networking(OptionsGroup):
    """Networking related stuff. Socket definition, binding and tuning."""
    
    class sockets:
        """Available socket types to use with ``.register_socket()``."""

        default = SocketDefault
        fastcgi = SocketFastcgi
        http = SocketHttp
        https = SocketHttps
        raw = SocketRaw
        scgi = SocketScgi
        shared = SocketShared
        udp = SocketUdp
        uwsgi = SocketUwsgi
        uwsgis = SocketUwsgis
        zeromq = SocketZeromq

        @classmethod
        def from_dsn(cls, dsn: str, *, allow_shared_sockets: bool | None = None) -> 'Socket':
            """Constructs socket configuration object from DSN.

            .. note:: This will also automatically use shared sockets
                to bind to priviledged ports when non root.

            :param dsn: Data source name, e.g:
                * http://127.0.0.1:8000
                * https://127.0.0.1:443?cert=/here/there.crt&key=/that/my.key

                .. note:: Some schemas:
                    fastcgi, http, https, raw, scgi, shared, udp, uwsgi, suwsgi, zeromq

            :param allow_shared_sockets: Allows using shared sockets to bind
                to privileged ports. If not provided automatic mode is enabled:
                shared are allowed if current user is not root.

            """
            split = urlsplit(dsn)

            sockets = {
                socket.name.replace('socket', '').rstrip('-'): socket
                for socket in cls.__dict__.values() if isinstance(socket, type) and issubclass(socket, Socket)}

            socket_kwargs = {
                'address': split.netloc,
            }
            socket_kwargs.update({key: val[0] for key, val in parse_qs(split.query).items()})
            socket = sockets[split.scheme]

            if split.port and split.port < 1024:

                if allow_shared_sockets is None:
                    allow_shared_sockets = (geteuid() != 0)

                if allow_shared_sockets:
                    new_shared = cls.shared(socket_kwargs['address'])
                    socket_kwargs['address'] = new_shared

            try:
                socket = socket(**socket_kwargs)

            except TypeError as e:
                raise ConfigurationError(
                    f'Unable to configure {socket.__name__} using `{dsn}` DSN: {e}') from None

            return socket

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sockets = []  # Registered sockets list.

    def set_basic_params(
            self,
            *,
            queue_size: int | None = None,
            freebind: bool | None = None,
            default_socket_type: str | None | type[Socket] = None,
            buffer_size: int | None = None
    ):
        """

        :param queue_size: Also known as a backlog. Every socket has an associated queue
            where request will be put waiting for a process to became ready to accept them. 
            When this queue is full, requests will be rejected.
            
            Default: 100 (an average value chosen by the maximum value allowed by default 
            by your kernel).

            .. note:: The maximum value is system/kernel dependent. Before increasing it you may 
                need to increase your kernel limit too.

        :param freebind: Put socket in freebind mode.
            Allows binding to non-existent network addresses.

            .. note:: Linux only.

        :param default_socket_type: Force the socket type as default.
            See ``.sockets``.

        :param buffer_size:
            Set the internal buffer max size - size of a request (request-body excluded),
            this generally maps to the size of request headers.  Default: 4096 bytes (4k) / page size.

            The amount of variables you can add per-request is limited by the uwsgi packet buffer ().
            You can increase it up to 65535 (64k) with this option.

            .. note:: If you receive a bigger request (for example with big cookies or query string)
                so that "invalid request block size" is logged in your logs you may need to increase it.
                It is a security measure too, so adapt to your app needs instead of maxing it out.

        """
        self._set('listen', queue_size)
        self._set('freebind', freebind, cast=bool)

        if default_socket_type:
            if issubclass(default_socket_type, Socket):
                default_socket_type = default_socket_type.name.replace('-socket', '')
            self._set('socket-protocol', default_socket_type)

        self._set('buffer-size', buffer_size)

        return self._section

    def set_socket_params(
            self,
            *,
            timeout: int | None = None,
            send_timeout: int | None = None,
            keep_alive: bool | None = None,
            no_defer_accept: bool | None = None,
            buffer_send: int | None = None,
            buffer_receive: int | None = None
    ):
        """Sets common socket params.

        :param timeout: Internal sockets timeout. Default: 4.

        :param send_timeout: Send (write) timeout in seconds.

        :param keep_alive: Enable TCP KEEPALIVEs.

        :param no_defer_accept: Disable deferred ``accept()`` on sockets
            by default (where available) uWSGI will defer the accept() of requests until some data
            is sent by the client (this is a security/performance measure).
            If you want to disable this feature for some reason, specify this option.

        :param buffer_send: Set SO_SNDBUF (bytes).

        :param buffer_receive: Set SO_RCVBUF (bytes).

        """
        self._set('socket-timeout', timeout)
        self._set('so-send-timeout', send_timeout)
        self._set('so-keepalive', keep_alive, cast=bool)
        self._set('no-defer-accept', no_defer_accept, cast=bool)
        self._set('socket-sndbuf', buffer_send)
        self._set('socket-rcvbuf', buffer_receive)

        return self._section

    def set_unix_socket_params(
            self,
            *,
            abstract: bool | None = None,
            permissions: str | None = None,
            owner: str | None = None,
            umask: str | None = None
    ):
        """Sets Unix-socket related params.

        :param abstract: Force UNIX socket into abstract mode (Linux only).

        :param permissions: UNIX sockets are filesystem objects that obey
            UNIX permissions like any other filesystem object.

            You can set the UNIX sockets' permissions with this option if your webserver
            would otherwise have no access to the uWSGI socket. When used without a parameter,
            the permissions will be set to 666. Otherwise the specified chmod value will be used.

        :param owner: Chown UNIX sockets.

        :param umask: Set UNIX socket umask.

        """
        self._set('abstract-socket', abstract, cast=bool)
        self._set('chmod-socket', permissions)
        self._set('chown-socket', owner)
        self._set('umask', umask)

        return self._section

    def set_bsd_socket_params(self, *, port_reuse: bool | None = None):
        """Sets BSD-sockets related params.

        :param port_reuse: Enable REUSE_PORT flag on socket to allow multiple
            instances binding on the same address (BSD only).

        """
        self._set('reuse-port', port_reuse, cast=bool)

        return self._section

    def _get_shared_socket_idx(self, shared: 'SocketShared'):
        return f'={self._sockets.index(shared)}'

    def register_socket(self, socket: Socket | list[Socket]):
        """Registers the given socket(s) for further use.

        :param socket: Socket type object. See ``.sockets``.

        """
        sockets = self._sockets

        for socket_ in listify(socket):

            uses_shared = isinstance(socket_.address, SocketShared)

            if uses_shared:
                # Handling shared sockets involves socket index resolution.

                shared_socket: SocketShared = socket_.address

                if shared_socket not in sockets:
                    self.register_socket(shared_socket)

                socket_.address = self._get_shared_socket_idx(shared_socket)

            socket_.address = self._section.replace_placeholders(socket_.address)
            self._set(socket_.name, socket_, multi=True)

            socket_._contribute_to_opts(self)

            bound_workers = socket_.bound_workers

            if bound_workers:
                self._set(
                    'map-socket', f"{len(sockets)}:{','.join(map(str, bound_workers))}",
                    multi=True)

            if not uses_shared:
                sockets.append(socket_)

        return self._section

    def set_ssl_params(
            self,
            *,
            verbose_errors: bool | None = None,
            sessions_cache: Strbool = None,
            sessions_timeout: int | None = None,
            session_context: str | None = None,
            raw_options: Intlist = None,
            dir_tmp: str | None = None,
            client_cert_var: str | None = None
    ):
        """

        :param verbose_errors: Be verbose about SSL errors.

        :param sessions_cache: Use uWSGI cache for ssl sessions storage.

            Accepts either bool or cache name string.

            * http://uwsgi.readthedocs.io/en/latest/SSLScaling.html

            .. warning:: Please be sure to configure cache before setting this.

        :param sessions_timeout: Set SSL sessions timeout in seconds. Default: 300.

        :param session_context: Session context identifying string. Can be set to static shared value
            to avoid session rejection.

            Default: a value built from the HTTP server address.

            * http://uwsgi.readthedocs.io/en/latest/SSLScaling.html#setup-2-synchronize-caches-of-different-https-routers

        :param raw_options: Set a raw ssl option by its numeric value.

        :param dir_tmp: Store ssl-related temp files (e.g. pem data) in the specified directory.

        :param client_cert_var: Export uWSGI variable ``HTTPS_CC`` containing the raw client certificate.

        """
        self._set('ssl-verbose', verbose_errors, cast=bool)
        self._set('ssl-sessions-use-cache', sessions_cache, cast=bool if isinstance(sessions_cache, bool) else None)
        self._set('ssl-sessions-timeout', sessions_timeout)

        for option in listify(raw_options):
            self._set('ssl-option', option, multi=True)

        self._set('ssl-tmp-dir', dir_tmp)

        self._set('https-session-context', session_context, plugin='http')
        self._set('https-export-cert', client_cert_var, plugin='http')

        return self._section

    def set_sni_params(
            self,
            name: str,
            *,
            cert: str,
            key: str,
            ciphers: str | None = None,
            client_ca: str | None = None,
            wildcard: bool = False
    ):
        """Allows setting Server Name Identification (virtual hosting for SSL nodes) params.

        * http://uwsgi.readthedocs.io/en/latest/SNI.html

        :param name: Node/server/host name.

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

        :param wildcard: Allow regular expressions in ``name`` (used for wildcard certificates).

        """
        command = 'sni'

        if wildcard:
            command += '-regexp'

        args = [item for item in (cert, key, ciphers, client_ca) if item is not None]

        self._set(command, f"{name} {','.join(args)}")

        return self._section

    def set_sni_dir_params(self, dir: str, ciphers: str | None = None):
        """Enable checking for cert/key/client_ca file in the specified directory
        and create a sni/ssl context on demand.

        Expected filenames:
            * <sni-name>.crt
            * <sni-name>.key
            * <sni-name>.ca - this file is optional

        * http://uwsgi.readthedocs.io/en/latest/SNI.html#massive-sni-hosting

        :param str dir:

        :param str ciphers: Ciphers [alias] string.

            Example:
                * DEFAULT
                * HIGH
                * DHE, EDH

            * https://www.openssl.org/docs/man1.1.0/apps/ciphers.html

        """
        self._set('sni-dir', dir)
        self._set('sni-dir-ciphers', ciphers)

        return self._section
