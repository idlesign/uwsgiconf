from ..base import OptionsGroup
from ..exceptions import ConfigurationError


class Networking(OptionsGroup):
    """Networking related stuff. Socket definition, binding and tuning."""

    SOCK_UWSGI = 'uwsgi'

    SOCK_HTTP = 'http'
    """Bind to the specified socket using HTTP"""

    SOCK_HTTP11 = 'http11'  # Keep-Alive

    SOCK_UDP = 'udp'
    """Run the udp server on the specified address.
    
    .. note:: Mainly useful for SNMP or shared UDP logging.
    
    """

    SOCK_FASTCGI = 'fastcgi'
    """Bind to the specified socket using FastCGI."""

    SOCK_SCGI = 'scgi'
    """Bind to the specified UNIX/TCP socket using SCGI protocol."""

    SOCK_RAW = 'raw'
    """Bind to the specified UNIX/TCP socket using RAW protocol."""

    SOCK_SHARED = 'shared'
    """Create a shared socket for advanced jailing or IPC purposes.
    
    Allows you to create a socket early in the server's startup 
    and use it after privileges drop or jailing. This can be used 
    to bind to privileged (<1024) ports.
    
    """

    SOCK_ZERO_MQ = 'zmq'
    """Introduce zeromq pub/sub pair."""

    MODE_SSL = '+ssl'
    """Use SSL."""

    MODE_NPH = '+nph'
    """Bind to the specified UNIX/TCP socket using nph mode."""

    MODE_PERSISTENT = '+persistent'
    """Use persistent uwsgi protocol (puwsgi)."""

    MODE_UNDEFERRED = '+undeferred'
    """Use shared socket undeferred mode."""

    def __init__(self, *args, **kwargs):
        super(Networking, self).__init__(*args, **kwargs)

        self._workers_binding = {}
        self._current_socket_idx = 0

    def set_basic_params(self, queue_size=None, freebind=None):
        """

        :param int queue_size: Every socket has an associated queue where request will be put waiting
            for a process to became ready to accept them. When this queue is full, requests will be rejected.
            Default 100.

            .. note:: The maximum value is system/kernel dependent.

        :param bool freebind: Put socket in freebind mode (Linux only).
            Allows binding to non-existent network addresses.

        """
        self._set('listen', queue_size)
        self._set('freebind', freebind, cast=bool)

        return self._section

    def set_socket_params(self, send_timeout=None, keep_alive=None, no_defer_accept=None):
        """Sets common socket params.

        :param int send_timeout: Send timeout in seconds.

        :param bool keep_alive: Enable TCP KEEPALIVEs.

        :param bool no_defer_accept: Disable deferred ``accept()`` on sockets
            by default (where available) uWSGI will defer the accept() of requests until some data
            is sent by the client (this is a security/performance measure).
            If you want to disable this feature for some reason, specify this option.

        """
        self._set('so-send-timeout', send_timeout)
        self._set('so-keepalive', keep_alive, cast=bool)
        self._set('no-defer-accept', no_defer_accept, cast=bool)

        return self._section

    def set_unix_socket_params(self, abstract=None, permissions=None, owner=None, umask=None):
        """Sets Unix-socket related params.

        :param bool abstract: Force UNIX socket into abstract mode (Linux only).

        :param str permissions: UNIX sockets are filesystem objects that obey
            UNIX permissions like any other filesystem object.

            You can set the UNIX sockets' permissions with this option if your webserver
            would otherwise have no access to the uWSGI socket. When used without a parameter,
            the permissions will be set to 666. Otherwise the specified chmod value will be used.

        :param str owner: Chown UNIX sockets.

        :param str umask: Set UNIX socket umask.

        """
        self._set('abstract-socket', abstract, cast=bool)
        self._set('chmod-socket', permissions)
        self._set('chown-socket', owner)
        self._set('umask', umask)

        return self._section

    def set_bsd_socket_params(self, port_reuse=None):
        """Sets BSD-sockets related params.

        :param bool port_reuse: Enable REUSE_PORT flag on socket to allow multiple
            instances binding on the same address (BSD only).

        """
        self._set('reuse-port', port_reuse, cast=bool)

        return self._section

    def register_sockets(self, *reg_dicts):
        """Convenience-method for batch socket registration.

        :param reg_dicts: Registration dictionaries with the same keys,
            which are accepted by .register_socket().

        """
        for reg_dict in reg_dicts:
            self.register_socket(**reg_dict)

        return self._section

    def register_socket(self, address='127.0.0.1:8000', type=SOCK_HTTP, mode=None, bound_workers=None):
        """Registers a socket.

        :param str address: Address to bind socket to.
            Examples:
                * socket file - /tmp/uwsgi.sock
                * all interfaces - 0.0.0.0:8080
                * all interfaces - :9090
                * ssl files - :9090,foobar.crt,foobar.key

        :param str type: Socket type. See Networking.SOCK_*

        :param str mode: Socket mode. See Networking.MODE_*

        :param str|int|list bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        """
        # todo maybe a convenience method for ssl - sertificate + key
        # todo *-modifier1

        mode = mode or ''

        param_name = {
            self.SOCK_UWSGI: {
                self.MODE_SSL: 'suwsgi-socket',
                self.MODE_PERSISTENT: 'puwsgi-socket',
            }.get(mode, 'uwsgi-socket'),  # Default: Bind to the specified socket with default protocol (see `protocol`)

            self.SOCK_HTTP: 'https-socket' if mode == self.MODE_SSL else 'http-socket',

            self.SOCK_HTTP11: 'http11-socket',

            self.SOCK_FASTCGI: 'fastcgi-nph-socket' if mode == self.MODE_NPH else 'fastcgi-socket',

            self.SOCK_SCGI: 'scgi-nph-socket' if mode == self.MODE_NPH else 'scgi-socket',

            self.SOCK_RAW: 'raw-socket',

            self.SOCK_SHARED: 'undeferred-shared-socket' if mode == self.MODE_UNDEFERRED else 'shared-socket',

            self.SOCK_UDP: 'upd',

            self.SOCK_ZERO_MQ: 'zeromq-socket',
        }.get(type)

        if param_name is None:
            raise ConfigurationError('Unknown socket type: `%s`' % type)

        self._set(param_name, address, multi=True)

        if bound_workers:
            if not isinstance(bound_workers, list):
                bound_workers = [bound_workers]

            self._set(
                'map-socket', '%s:%s' % (self._current_socket_idx, ','.join(map(str, bound_workers))),
                multi=True)

            self._current_socket_idx += 1

        return self._section
