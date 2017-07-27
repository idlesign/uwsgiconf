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

        :param str|unicode owner: Chown UNIX sockets.

        :param str|unicode umask: Set UNIX socket umask.

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

        :param str|unicode address: Address to bind socket to.
            Examples:
                * socket file - /tmp/uwsgi.sock
                * all interfaces - 0.0.0.0:8080
                * all interfaces - :9090
                * ssl files - :9090,foobar.crt,foobar.key

        :param str|unicode type: Socket type. See Networking.sockets

        :param str|unicode mode: Socket mode. See Networking.modes

        :param  str|unicode|int|list bound_workers: Map socket to specific workers.
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

    def set_ssl_params(
            self, verbose_errors=None,
            sessions_cache=None, sessions_timeout=None, session_context=None,
            raw_options=None, dir_tmp=None, client_cert_var=None):
        """

        :param bool verbose_errors: Be verbose about SSL errors.

        :param str|unicode|bool sessions_cache: Use uWSGI cache for ssl sessions storage.

            Accepts either bool or cache name string.

            * http://uwsgi.readthedocs.io/en/latest/SSLScaling.html

            .. warning:: Please be sure to configure cache before setting this.

        :param int sessions_timeout: Set SSL sessions timeout in seconds. Default: 300.

        :param str|unicode session_context: Session context identifying string. Can be set to static shared value
            to avoid session rejection.

            Default: a value built from the HTTP server address.

            * http://uwsgi.readthedocs.io/en/latest/SSLScaling.html#setup-2-synchronize-caches-of-different-https-routers

        :param int|list[int] raw_options: Set a raw ssl option by its numeric value.

        :param str|unicode dir_tmp: Store ssl-related temp files (e.g. pem data) in the specified directory.

        :param str|unicode client_cert_var: Export uWSGI variable ``HTTPS_CC`` containing the raw client certificate.

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

    def set_sni_params(self, name, cert, key, ciphers=None, client_ca=None, wildcard=False):
        """Allows setting Server Name Identification (virtual hosting for SSL nodes) params.

        * http://uwsgi.readthedocs.io/en/latest/SNI.html

        :param str|unicode name: Node/server/host name.

        :param str|unicode cert: Certificate file.

        :param str|unicode key: Private key file.

        :param str|unicode ciphers: Ciphers [alias] string.

            Example:
                * DEFAULT
                * HIGH
                * DHE, EDH

            * https://www.openssl.org/docs/man1.1.0/apps/ciphers.html

        :param str|unicode client_ca: Client CA file for client-based auth.

        :param bool wildcard: Allow regular expressions in ``name`` (used for wildcard certificates).

        """
        command = 'sni'

        if wildcard:
            command += '-regexp'

        args = [item for item in (cert, key, ciphers, client_ca) if item is not None]

        self._set(command, '%s %s' % (name, ','.join(args)))

        return self._section

    def set_sni_dir_params(self, dir, ciphers=None):
        """Enable checking for cert/key/client_ca file in the specified directory
        and create a sni/ssl context on demand.

        Expected filenames:
            * <sni-name>.crt
            * <sni-name>.key
            * <sni-name>.ca - this file is optional

        * http://uwsgi.readthedocs.io/en/latest/SNI.html#massive-sni-hosting

        :param str|unicode dir:

        :param str|unicode ciphers: Ciphers [alias] string.

            Example:
                * DEFAULT
                * HIGH
                * DHE, EDH

            * https://www.openssl.org/docs/man1.1.0/apps/ciphers.html

        """
        self._set('sni-dir', dir)
        self._set('sni-dir-ciphers', ciphers)

        return self._section
