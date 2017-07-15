from ..base import OptionsGroup
from ..exceptions import ConfigurationError
from ..utils import listify


class Networking(OptionsGroup):
    """Networking related stuff. Socket definition, binding and tuning."""
    
    class socket_types(object):
        """Available socket types to use with ``.register_socket()``."""
    
        DEFAULT = 'default'
        """Bind using default protocol. See ``default_protocol`` option."""

        UWSGI = 'uwsgi'

        HTTP = 'http'
        """Bind to the specified socket using HTTP"""
    
        HTTP11 = 'http11'  # Keep-Alive
    
        UDP = 'udp'
        """Run the udp server on the specified address.
        
        .. note:: Mainly useful for SNMP or shared UDP logging.
        
        """
    
        FASTCGI = 'fastcgi'
        """Bind to the specified socket using FastCGI."""
    
        SCGI = 'scgi'
        """Bind to the specified UNIX/TCP socket using SCGI protocol."""
    
        RAW = 'raw'
        """Bind to the specified UNIX/TCP socket using RAW protocol."""
    
        SHARED = 'shared'
        """Create a shared socket for advanced jailing or IPC purposes.
        
        Allows you to create a socket early in the server's startup 
        and use it after privileges drop or jailing. This can be used 
        to bind to privileged (<1024) ports.
        
        """
    
        ZERO_MQ = 'zmq'
        """Introduce zeromq pub/sub pair."""

    class modes(object):
        """Available socket modes to use with ``.register_socket()``."""

        SSL = '+ssl'
        """Use SSL."""

        NPH = '+nph'
        """Bind to the specified UNIX/TCP socket using nph mode."""

        PERSISTENT = '+persistent'
        """Use persistent uwsgi protocol (puwsgi)."""

        UNDEFERRED = '+undeferred'
        """Use shared socket undeferred mode."""

    def __init__(self, *args, **kwargs):
        super(Networking, self).__init__(*args, **kwargs)

        self._workers_binding = {}
        self._current_socket_idx = 0

    def set_basic_params(self, queue_size=None, freebind=None, default_socket_type=None):
        """

        :param int queue_size: Every socket has an associated queue where request will be put waiting
            for a process to became ready to accept them. When this queue is full, requests will be rejected.
            Default 100.

            .. note:: The maximum value is system/kernel dependent.

        :param bool freebind: Put socket in freebind mode.
            Allows binding to non-existent network addresses.

            .. note:: Linux only.

        :param str|unicode default_socket_type: Force the socket type as default.
            See ``.socket_types``.

        """
        self._set('listen', queue_size)
        self._set('freebind', freebind, cast=bool)
        self._set('socket-protocol', default_socket_type)

        return self._section

    def set_socket_params(
            self, send_timeout=None, keep_alive=None, no_defer_accept=None,
            buffer_send=None, buffer_receive=None):
        """Sets common socket params.

        :param int send_timeout: Send (write) timeout in seconds.

        :param bool keep_alive: Enable TCP KEEPALIVEs.

        :param bool no_defer_accept: Disable deferred ``accept()`` on sockets
            by default (where available) uWSGI will defer the accept() of requests until some data
            is sent by the client (this is a security/performance measure).
            If you want to disable this feature for some reason, specify this option.

        :param int buffer_send: Set SO_SNDBUF (bytes).

        :param int buffer_receive: Set SO_RCVBUF (bytes).

        """
        self._set('so-send-timeout', send_timeout)
        self._set('so-keepalive', keep_alive, cast=bool)
        self._set('no-defer-accept', no_defer_accept, cast=bool)
        self._set('socket-sndbuf', buffer_send)
        self._set('socket-rcvbuf', buffer_receive)

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

    def register_socket(self, address, type=socket_types.DEFAULT, mode=None, bound_workers=None):
        """Registers a socket.

        :param str address: Address to bind socket to.
            Examples:
                * socket file - /tmp/uwsgi.sock
                * all interfaces - 0.0.0.0:8080
                * all interfaces - :9090
                * ssl files - :9090,foobar.crt,foobar.key

        :param str type: Socket type. See Networking.sockets

        :param str mode: Socket mode. See Networking.modes

        :param str|int|list bound_workers: Map socket to specific workers.
            As you can bind a uWSGI instance to multiple sockets, you can use this option to map
            specific workers to specific sockets to implement a sort of in-process Quality of Service scheme.
            If you host multiple apps in the same uWSGI instance, you can easily dedicate resources to each of them.

        """
        # todo maybe a convenience method for ssl - sertificate + key
        # todo *-modifier1

        mode = mode or ''

        param_name = {
            self.socket_types.UWSGI: {
                self.modes.SSL: 'suwsgi-socket',
                self.modes.PERSISTENT: 'puwsgi-socket',

            }.get(mode, 'uwsgi-socket'),
            # Default: Bind to the specified socket with default protocol (see `protocol/socket-protocol`)
            # socket-protocol = 0,uwsgi
            # socket-protocol = 3,uwsgidump

            self.socket_types.HTTP: 'https-socket' if mode == self.modes.SSL else 'http-socket',

            self.socket_types.HTTP11: 'http11-socket',

            self.socket_types.FASTCGI: 'fastcgi-nph-socket' if mode == self.modes.NPH else 'fastcgi-socket',

            self.socket_types.SCGI: 'scgi-nph-socket' if mode == self.modes.NPH else 'scgi-socket',

            self.socket_types.RAW: 'raw-socket',

            self.socket_types.SHARED: 'undeferred-shared-socket' if mode == self.modes.UNDEFERRED else 'shared-socket',

            self.socket_types.UDP: 'upd',

            self.socket_types.ZERO_MQ: 'zeromq-socket',

            self.socket_types.DEFAULT: 'socket',

        }.get(type)

        if param_name is None:
            raise ConfigurationError('Unknown socket type: `%s`' % type)

        self._set(param_name, address, multi=True)

        if bound_workers:
            bound_workers = listify(bound_workers)

            self._set(
                'map-socket', '%s:%s' % (self._current_socket_idx, ','.join(map(str, bound_workers))),
                multi=True)

            self._current_socket_idx += 1

        return self._section
