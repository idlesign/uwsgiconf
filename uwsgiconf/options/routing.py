from ..base import OptionsGroup, ParametrizedValue
from ..exceptions import ConfigurationError
from ..utils import listify, make_key_val_string, filter_locals


class Var(object):

    tpl = '%s'

    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self.tpl % self._name


class RouteAction(ParametrizedValue):

    pass


class ActionFlush(RouteAction):
    """Send the current contents of the transformation buffer
    to the client (without clearing the buffer).

    * http://uwsgi.readthedocs.io/en/latest/Transformations.html#flushing-magic

    """
    name = 'flush'

    def __init__(self):
        super(ActionFlush, self).__init__()


class ActionGzip(RouteAction):
    """Encodes the response buffer to gzip."""

    name = 'gzip'
    plugin = 'transformation_gzip'

    def __init__(self):
        super(ActionGzip, self).__init__()


class ActionToFile(RouteAction):
    """Used for caching a response buffer into a static file."""

    name = 'tofile'
    plugin = 'transformation_tofile'

    def __init__(self, filename, mode=None):
        arg = make_key_val_string(locals())
        super(ActionToFile, self).__init__(arg)


class ActionUpper(RouteAction):
    """Transforms each character in uppercase.

    Mainly as an example of transformation plugin.

    """
    name = 'toupper'
    plugin = 'transformation_toupper'

    def __init__(self):
        super(ActionUpper, self).__init__()


class ActionChunked(RouteAction):
    """Encodes the output in HTTP chunked."""

    name = 'chunked'

    def __init__(self):
        super(ActionChunked, self).__init__()


class ActionTemplate(RouteAction):
    """Allows using a template file to expose everything
    from internal routing system into it.

    * http://uwsgi.readthedocs.io/en/latest/Changelog-1.9.19.html#the-template-transformation

    """
    name = 'template'

    def __init__(self):
        super(ActionTemplate, self).__init__()


class ActionFixContentLen(RouteAction):
    """Fixes Content-length header."""

    name = 'fixcl'

    def __init__(self, add_header=False):
        """
        :param bool add_header: Force header add instead of plain fix of existing header.
        """
        if add_header:
            self.name = 'forcexcl'

        super(ActionFixContentLen, self).__init__()


class ActionDoContinue(RouteAction):
    """Stop scanning the internal routing table
    and continue to the selected request handler.

    """
    name = 'continue'

    def __init__(self):
        super(ActionDoContinue, self).__init__()


class ActionDoBreak(RouteAction):
    """Stop scanning the internal routing table and close the request."""

    name = 'break'

    def __init__(self, code, return_body=False):
        """
        :param int code: HTTP code

        :param return_body: Uses uWSGI's built-in status code and returns
            both status code and message body.

        """
        if return_body:
            self.name = 'return'

        super(ActionDoBreak, self).__init__(code)


class ActionLog(RouteAction):
    """Print the specified message in the logs or
    do not log a request is ``message`` is ``None``.

    """
    name = 'log'

    def __init__(self, message):
        """

        :param str|unicode|None message: Message to add into log.
            If ``None`` logging will be disabled for this request.

        """
        if message is None:
            self.name = 'donotlog'

        super(ActionLog, self).__init__(message)


class ActionOffloadOff(RouteAction):
    """Do not use offloading."""

    name = 'donotoffload'

    def __init__(self):
        super(ActionOffloadOff, self).__init__()


class ActionAddVarLog(RouteAction):
    """Add the specified logvar."""

    name = 'logvar'

    def __init__(self, name, val):
        """
        :param str|unicode name: Variable name.

        :param val: Variable value.
        """
        super(ActionAddVarLog, self).__init__(name, val)


class ActionDoGoto(RouteAction):
    """Make a forward jump to the specified label or rule position."""

    name = 'goto'

    def __init__(self, where):
        """
        :param str|unicode|int where: Rule number of label to go to.
        """
        super(ActionDoGoto, self).__init__(where)


class ActionAddVarCgi(RouteAction):
    """Add the specified CGI (environment) variable to the request."""

    name = 'addvar'

    def __init__(self, name, val):
        """
        :param str|unicode name: Variable name.

        :param val: Variable value.
        """
        super(ActionAddVarCgi, self).__init__(name, val)


class ActionHeaderAdd(RouteAction):
    """Add the specified HTTP header to the response."""

    name = 'addheader'

    def __init__(self, name, val):
        """
        :param str|unicode name: Header name.

        :param val: Header value.
        """
        name += ':'

        super(ActionHeaderAdd, self).__init__(name, val)


class ActionHeaderRemove(RouteAction):
    """Remove the specified HTTP header from the response."""

    name = 'delheader'

    def __init__(self, name):
        """
        :param str|unicode name: Header name.
        """
        super(ActionHeaderRemove, self).__init__(name)


class ActionHeadersOff(RouteAction):
    """Disable headers."""

    name = 'disableheaders'

    def __init__(self):
        super(ActionHeadersOff, self).__init__()


class ActionHeadersReset(RouteAction):
    """Clear the response headers, setting a new HTTP status code,
    useful for resetting a response.

    """
    name = 'clearheaders'

    def __init__(self, code):
        """
        :param int code: HTTP code.
        """
        super(ActionHeadersReset, self).__init__(code)


class ActionSignal(RouteAction):
    """Raise the specified uwsgi signal."""

    name = 'signal'

    def __init__(self, num):
        """
        :param int num: Signal number.
        """
        super(ActionSignal, self).__init__(num)


class ActionSend(RouteAction):
    """Extremely advanced (and dangerous) function allowing you
    to add raw data to the response.

    """
    name = 'send'

    def __init__(self, data, crnl=False):
        """
        :param data: Data to add to response.
        :param bool crnl: Add carriage return and new line.
        """
        if crnl:
            self.name = 'send-crnl'
        super(ActionSend, self).__init__(data)


class ActionRedirect(RouteAction):
    """Return a HTTP 301/302 Redirect to the specified URL."""

    name = 'redirect-302'
    plugin = 'router_redirect'

    def __init__(self, url, permanent=False):
        """
        :param str| unicode url: URL to redirect to.
        :param bool permanent: If ``True`` use 301, otherwise 302.
        """
        if permanent:
            self.name = 'redirect-301'

        super(ActionRedirect, self).__init__(url)


class ActionRewrite(RouteAction):
    """A rewriting engine inspired by Apache mod_rewrite.

    Rebuild PATH_INFO and QUERY_STRING according to the specified rules
    before the request is dispatched to the request handler.

    """
    name = 'rewrite'
    plugin = 'router_rewrite'

    def __init__(self, rule, do_continue=False):
        """
        :param str|unicode rule: A rewrite rule.

        :param bool do_continue: Stop request processing
            and continue to the selected request handler.

        """
        if do_continue:
            self.name = 'rewrite-last'

        super(ActionRewrite, self).__init__(rule)


class ActionRouteUwsgi(RouteAction):
    """Rewrite the modifier1, modifier2 and optionally UWSGI_APPID values of a request
    or route the request to an external uwsgi server.

    """
    name = 'uwsgi'
    plugin = 'router_uwsgi'
    args_joiner = ','

    def __init__(self, external_address='', mod1='', mod2='', app=''):
        """
        :param str|unicode external_address: External uWSGI server address (host:port).
        :param str|unicode mod1: Set modifier 1.
        :param str|unicode mod2: Set modifier 2.
        :param str|unicode app: Set ``UWSGI_APPID``.
        """
        super(ActionRouteUwsgi, self).__init__(external_address, mod1, mod2, app)


class ActionRouteExternal(RouteAction):
    """Route the request to an external HTTP server."""

    name = 'http'
    plugin = 'router_http'
    args_joiner = ','

    def __init__(self, address, host_header=None):
        """
        :param str|unicode address: External HTTP address (host:port)

        :param str|unicode host_header: HOST header value.
        """
        super(ActionRouteExternal, self).__init__(address, host_header)


class ActionAlarm(RouteAction):
    """Triggers an alarm.

    * http://uwsgi.readthedocs.io/en/latest/Changelog-1.9.6.html#the-alarm-routing-action

    """
    name = 'alarm'

    def __init__(self, name, message):
        """
        :param str|unicode name: Alarm name

        :param str|unicode message: Message to pass into alarm.
        """
        super(ActionAlarm, self).__init__(name, message)


class ActionServeStatic(RouteAction):
    """Serve a static file from the specified physical path."""

    name = 'static'
    plugin = 'router_static'

    def __init__(self, fpath):
        """
        :param str|unicode fpath: Static file path.
        """
        super(ActionServeStatic, self).__init__(fpath)


class ActionAuthBasic(RouteAction):
    """Use Basic HTTP Auth."""

    name = 'basicauth'
    plugin = 'router_basicauth'
    args_joiner = ','

    def __init__(self, realm, user=None, password=None, do_next=False):
        """
        :param str|unicode realm:

        :param str|unicode user:

        :param str|unicode password: Password or htpasswd-like file.

        :param bool do_next: Allow next rule.
        """
        if do_next:
            self.name = 'basicauth-next'

        user_password = []

        if user:
            user += ':'
            user_password.append(user)

        if password:
            user_password.append(password)

        super(ActionAuthBasic, self).__init__(realm, ''.join(user_password) if user_password else None)


class AuthLdap(RouteAction):
    """Use Basic HTTP Auth."""

    name = 'ldapauth'
    plugin = 'ldap'
    args_joiner = ','

    def __init__(
            self, realm, address, base_dn=None, bind_dn=None, bind_password=None,
            filter=None, login_attr=None, log_level=None,
            do_next=False):
        """

        :param str|unicode realm:

        :param str|unicode address: LDAP server URI

        :param str|unicode base_dn: Base DN used when searching for users.

        :param str|unicode bind_dn: DN used for binding.
            Required if the LDAP server does not allow anonymous searches.

        :param str|unicode bind_password: Password for the ``bind_dn`` user.

        :param str|unicode filter: Filter used when searching for users. Default: ``(objectClass=*)``

        :param str|unicode login_attr: LDAP attribute that holds user login. Default: ``uid``.

        :param str|unicode log_level: Log level.

            Supported values:
                * 0 - don't log any binds
                * 1 - log authentication errors,
                * 2 - log both successful and failed binds

        :param bool do_next: Allow next rule.
        """
        arg = make_key_val_string(
            filter_locals(locals(), drop=['realm', 'do_next']),
            aliases={
                'address': 'url',
                'base_dn': 'basedn',
                'bind_dn': 'binddn',
                'bind_password': 'bindpw',
                'login_attr': 'attr',
                'log_level': 'loglevel',
            },
            items_separator=';'
        )

        if do_next:
            self.name = 'ldapauth-next'

        super(AuthLdap, self).__init__(realm, arg)


class ActionSetHarakiri(RouteAction):
    """Set harakiri timeout for the current request."""

    name = 'harakiri'

    def __init__(self, timeout):
        """
        :param int timeout:
        """
        super(ActionSetHarakiri, self).__init__(timeout)


class ActionDirChange(RouteAction):
    """Changes a directory."""

    name = 'chdir'

    def __init__(self, dir):
        """
        :param str|unicode dir: Directory to change into.
        """
        super(ActionDirChange, self).__init__(dir)


class ActionSetVarUwsgiAppid(RouteAction):
    """Set UWSGI_APPID"""

    name = 'setapp'

    def __init__(self, app):
        """
        :param str|unicode app: Application ID.
        """
        super(ActionSetVarUwsgiAppid, self).__init__(app)


class ActionSetVarRemoteUser(RouteAction):
    """Set REMOTE_USER"""

    name = 'setuser'

    def __init__(self, user):
        """
        :param str|unicode user: Username.
        """
        super(ActionSetVarRemoteUser, self).__init__(user)


class ActionSetVarUwsgiHome(RouteAction):
    """Set UWSGI_HOME"""

    name = 'sethome'

    def __init__(self, dir):
        """
        :param str|unicode dir: Directory to make a new home.
        """
        super(ActionSetVarUwsgiHome, self).__init__(dir)


class ActionSetVarUwsgiScheme(RouteAction):
    """Set UWSGI_SCHEME.

    * http://uwsgi.readthedocs.io/en/latest/Changelog-1.9.6.html#configuring-dynamic-apps-with-internal-routing

    """
    name = 'setscheme'

    def __init__(self, value):
        """
        :param str|unicode value:
        """
        super(ActionSetVarUwsgiScheme, self).__init__(value)


class ActionSetVarScriptName(RouteAction):
    """Set SCRIPT_NAME"""

    name = 'setscriptname'

    def __init__(self, name):
        """
        :param str|unicode name: Script name
        """
        super(ActionSetVarScriptName, self).__init__(name)


class ActionSetVarRequestMethod(RouteAction):
    """Set REQUEST_METHOD"""

    name = 'setmethod'

    def __init__(self, name):
        """
        :param str|unicode name: Method name.
        """
        super(ActionSetVarRequestMethod, self).__init__(name)


class ActionSetVarRequestUri(RouteAction):
    """Set REQUEST_URI"""

    name = 'seturi'

    def __init__(self, value):
        """
        :param str|unicode value: URI
        """
        super(ActionSetVarRequestUri, self).__init__(value)


class ActionSetVarRemoteAddr(RouteAction):
    """Set REMOTE_ADDR"""

    name = 'setremoteaddr'

    def __init__(self, value):
        """
        :param str|unicode value: Address.
        """
        super(ActionSetVarRemoteAddr, self).__init__(value)


class ActionSetVarPathInfo(RouteAction):
    """Set PATH_INFO"""

    name = 'setpathinfo'

    def __init__(self, value):
        """
        :param str|unicode value: New info.
        """
        super(ActionSetVarPathInfo, self).__init__(value)


class ActionSetVarDocumentRoot(RouteAction):
    """Set DOCUMENT_ROOT"""

    name = 'setdocroot'

    def __init__(self, value):
        """
        :param str|unicode value:
        """
        super(ActionSetVarDocumentRoot, self).__init__(value)


class ActionSetUwsgiProcessName(RouteAction):
    """Set uWSGI process name."""

    name = 'setprocname'

    def __init__(self, name):
        """
        :param str|unicode name: New process name.
        """
        super(ActionSetUwsgiProcessName, self).__init__(name)


class ActionFixVarPathInfo(RouteAction):
    """Fixes PATH_INFO taking into account script name.

    This action allows you to set SCRIPT_NAME in nginx without bothering
    to rewrite the PATH_INFO (something nginx cannot afford).

    * http://uwsgi.readthedocs.io/en/latest/Changelog-2.0.11.html#fixpathinfo-routing-action

    """
    name = 'fixpathinfo'

    def __init__(self):
        super(ActionFixVarPathInfo, self).__init__()


class ActionSetScriptFile(RouteAction):
    """Set script file.

    * http://uwsgi.readthedocs.io/en/latest/Changelog-1.9.6.html#configuring-dynamic-apps-with-internal-routing

    """
    name = 'setfile'

    def __init__(self, fpath):
        """
        :param str|unicode fpath: File path.
        """
        super(ActionSetScriptFile, self).__init__(fpath)


class SubjectBuiltin(object):

    name = None

    def __init__(self, regexp):
        self.regexp = regexp


class SubjectCustom(ParametrizedValue):
    """Represents a routing subject that supports various check."""

    args_joiner = ';'

    def __init__(self, subject, negate=False):
        """
        :param Var|str|unicode subject: Handwritten subject or a Var heir representing it.

        :param bool negate: Use to negate subject for rule.
            .. note:: You can also use tilde (~) instead of this argument for nagation.

        """
        self._subject = subject
        self.negate = negate
        super(SubjectCustom, self).__init__()

    def __invert__(self):
        self.negate = True
        return self

    def _setup(self, name, arg=None):
        self.name = '%s' % name
        self.args = [self._subject, arg]
        return self

    def exists(self):
        """Check if the subject exists in the filesystem."""
        return self._setup('exists')

    def isfile(self):
        """Check if the subject is a file."""
        return self._setup('isfile')

    def isdir(self):
        """Check if the subject is a directory."""
        return self._setup('isdir')

    def islink(self):
        """Check if the subject is a link."""
        return self._setup('islink')

    def isexec(self):
        """Check if the subject is an executable file."""
        return self._setup('isexec')

    def islord(self):
        """Check if the subject is a Legion Lord."""
        return self._setup('lord')

    def contains_ipv4(self):
        """Check if the subject is ip v4."""
        return self._setup('ipv4in')

    def contains_ipv6(self):
        """Check if the subject is ip v6."""
        return self._setup('ipv6in')

    def eq(self, val):
        """Check if the subject is equal to the specified pattern."""
        return self._setup('eq', val)

    def ge(self, val):
        """Check if the subject is greater than or equal to the specified pattern."""
        return self._setup('ishigherequal', val)

    def le(self, val):
        """Check if the subject is less than or equal to the specified pattern."""
        return self._setup('islowerequal', val)

    def gt(self, val):
        """Check if the subject is greater than the specified pattern."""
        return self._setup('ishigher', val)

    def lt(self, val):
        """Check if the subject is less than the specified pattern."""
        return self._setup('islower', val)

    def startswith(self, val):
        """Check if the subject starts with the specified pattern."""
        return self._setup('startswith', val)

    def endswith(self, val):
        """Check if the subject ends with the specified pattern."""
        return self._setup('endswith', val)

    def matches(self, regexp):
        """Check if the subject matches the specified regexp."""
        return self._setup('regexp', regexp)

    def isempty(self):
        """Check if the subject is empty."""
        return self._setup('empty')

    def contains(self, val):
        """Check if the subject contains the specified pattern."""
        return self._setup('contains', val)


class RouteRule(object):
    """Represents a routing rule."""

    class vars(object):
        """Routing variables."""

        class request(Var):
            """Returns request variable. Examples: PATH_INFO, SCRIPT_NAME, REQUEST_METHOD."""
            tpl = '${%s}'

        class metric(Var):
            """Returns metric (see ``monitoring``) variable."""
            tpl = '${metric[%s]}'

        class cookie(Var):
            """Returns cookie variable"""
            tpl = '${cookie[%s]}'

        class query(Var):
            """Returns query string variable."""
            tpl = '${qs[%s]}'

        class uwsgi(Var):
            """Returns internal uWSGI information.

             Supported variables:
                * wid
                * pid
                * uuid
                * status

            """
            tpl = '${uwsgi[%s]}'

        class time(Var):
            """Returns time/date in various forms.

            Supported variables:
                * unix

            """
            tpl = '${time[%s]}'

        class httptime(Var):
            """Returns http date adding the numeric argument (if specified)
            to the current time (use empty arg for current server time).

            """
            tpl = '${httptime[%s]}'

    class var_functions(object):
        """Functions that can be applied to variables."""

        class mime(Var):
            """Returns mime type of a variable."""
            tpl = '${mime[%s]}'

        class math(Var):
            """Perform a math operation. Example: CONTENT_LENGTH+1

            Supported operations: + - * /

            .. warning:: Requires matheval support.

            """
            tpl = '${math[%s]}'

        class base64(Var):
            """Encodes the specified var in base64"""
            tpl = '${base64[%s]}'

        class hex(Var):
            """Encodes the specified var in hex."""
            tpl = '${hex[%s]}'

        class upper(Var):
            """Uppercase the specified var."""
            tpl = '${upper[%s]}'

        class lower(Var):
            """Lowercase the specified var."""
            tpl = '${lower[%s]}'

    class stages(object):
        """During the request cycle, various stages (aka chains) are processed.

        Chains can be "recursive". A recursive chain can be called multiple times
        in a request cycle.

        """

        REQUEST = ''
        """Applied before the request is passed to the plugin."""

        ERROR = 'error'
        """Applied as soon as an HTTP status code is generate. **Recursive chain**."""

        RESPONSE = 'response'
        """Applied after the last response header has been generated (just before sending the body)."""

        FINAL = 'final'
        """Applied after the response has been sent to the client."""

    class subjects(object):
        """Routing subjects. These can be request's variables or other entities.

        .. note:: Non-custom subjects (uppercased) can be pre-optimized (during startup)
            and should be used for performance reasons.

        """
        custom = SubjectCustom

        class PATH_INFO(SubjectBuiltin):
            """Default subject, maps to PATH_INFO."""

            name = ''

        class REQUEST_URI(SubjectBuiltin):
            """Checks REQUEST_URI for a value."""

            name = 'uri'

        class QUERY_STRING(SubjectBuiltin):
            """Checks QUERY_STRING for a value."""

            name = 'qs'

        class REMOTE_ADDR(SubjectBuiltin):
            """Checks REMOTE_ADDR for a value."""

            name = 'remote-addr'

        class REMOTE_USER(SubjectBuiltin):
            """Checks REMOTE_USER for a value."""

            name = 'remote-user'

        class HTTP_HOST(SubjectBuiltin):
            """Checks HTTP_HOST for a value."""

            name = 'host'

        class HTTP_REFERER(SubjectBuiltin):
            """Checks HTTP_REFERER for a value."""

            name = 'referer'

        class HTTP_USER_AGENT(SubjectBuiltin):
            """Checks HTTP_USER_AGENT for a value."""

            name = 'user-agent'

        class STATUS(SubjectBuiltin):
            """Checks HTTP response status code.

            .. warning:: Not available in the request chain.

            """
            name = 'status'

    class transforms(object):
        """A transformation is like a filter applied to the response
        generated by your application.

        Transformations can be chained (the output of a transformation will be the input of the following one)
        and can completely overwrite response headers.

        * http://uwsgi.readthedocs.io/en/latest/Transformations.html

        """
        chunked = ActionChunked
        fix_content_len = ActionFixContentLen
        flush = ActionFlush
        gzip = ActionGzip
        template = ActionTemplate
        to_file = ActionToFile
        upper = ActionUpper

        # todo Consider adding the following and some others from sources (incl. plugins):
        # xslt, cachestore, memcachedstore, redisstore, rpc, lua

    class actions(object):
        """Actions available for routing rules.

        Values returned by actions:

            * ``NEXT`` - continue to the next rule
            * ``CONTINUE`` - stop scanning the internal routing table and run the request
            * ``BREAK`` - stop scanning the internal routing table and close the request
            * ``GOTO x`` - go to rule ``x``

        """
        add_var_cgi = ActionAddVarCgi
        add_var_log = ActionAddVarLog
        alarm = ActionAlarm
        auth_basic = ActionAuthBasic
        auth_ldap = AuthLdap
        dir_change = ActionDirChange
        do_break = ActionDoBreak
        do_continue = ActionDoContinue
        do_goto = ActionDoGoto
        fix_var_path_info = ActionFixVarPathInfo
        header_add = ActionHeaderAdd
        header_remove = ActionHeaderRemove
        headers_off = ActionHeadersOff
        headers_reset = ActionHeadersReset
        log = ActionLog
        offload_off = ActionOffloadOff
        redirect = ActionRedirect
        rewrite = ActionRewrite
        route_external = ActionRouteExternal
        route_uwsgi = ActionRouteUwsgi
        send = ActionSend
        serve_static = ActionServeStatic
        set_harakiri = ActionSetHarakiri
        set_script_file = ActionSetScriptFile
        set_uwsgi_process_name = ActionSetUwsgiProcessName
        set_var_document_root = ActionSetVarDocumentRoot
        set_var_path_info = ActionSetVarPathInfo
        set_var_remote_addr = ActionSetVarRemoteAddr
        set_var_remote_user = ActionSetVarRemoteUser
        set_var_request_method = ActionSetVarRequestMethod
        set_var_request_uri = ActionSetVarRequestUri
        set_var_script_name = ActionSetVarScriptName
        set_var_uwsgi_appid = ActionSetVarUwsgiAppid
        set_var_uwsgi_home = ActionSetVarUwsgiHome
        set_var_uwsgi_scheme = ActionSetVarUwsgiScheme
        signal = ActionSignal

        # todo Consider adding the following and some others from sources (incl. plugins):
        # cachestore, cacheset, memcached,
        # router_cache: cache, cache-continue, cachevar, cacheinc, cachedec, cachemul, cachediv
        # rpc,
        # rpc: call, rpcret, rpcnext, rpcraw, rpcvar,
        # access, spnego, radius
        # xslt, ssi, gridfs
        # cgi: cgi, cgihelper
        # router_access: access,
        # proxyhttp -router_http, proxyuwsgi -router_uwsgi, xattr -xattr
        # router_memcached: memcached, memcached-continue, memcachedstore
        # router_redis: redis, redis-continue, redisstore

    def __init__(self, action, subject=subjects.PATH_INFO('(.*)'), stage=stages.REQUEST):
        """
        :param RouteAction action: Action (or transformation) to perfrom.
            See ``.actions`` and ``.transforms``.

        :param SubjectCustom|SubjectBuiltin subject: Subject to verify before action is performed.
            See ``.subjects``.

        :param str|unicode stage: Stage on which the action needs to be performed.
            See ``.stages``.

        """
        if subject is None:
            subject = 'run'  # always run the specified route action

        subject_rule = ''

        self._custom_subject = isinstance(subject, SubjectCustom)

        if self._custom_subject:
            subject_rule = subject
            subject = 'if-not' if subject.negate else 'if'

        elif isinstance(subject, SubjectBuiltin):
            subject_rule = subject.regexp
            subject = subject.name

        self.command_label = ('%s-route-label' % stage).strip('-')
        self.command = ('%s-route-%s' % (stage, subject)).strip('-')
        self.value = subject_rule, action


class Routing(OptionsGroup):
    """Routing subsystem.

    You can use the internal routing subsystem to dynamically alter the way requests are handled.

    .. note:: Since 1.9

    * http://uwsgi.readthedocs.io/en/latest/InternalRouting.html
    * http://uwsgi.readthedocs.io/en/latest/Transformations.html

    """

    route_rule = RouteRule

    def register_route(self, route_rules, label=None):
        """Registers a routing rule.

        :param RouteRule|list[RouteRule] route_rules:

        :param str|unicode label: Label to mark the given set of rules.
            This can be used in conjunction with ``do_goto`` rule action.

            * http://uwsgi.readthedocs.io/en/latest/InternalRouting.html#goto

        """
        route_rules = listify(route_rules)

        if route_rules and label:
            self._set(route_rules[0].command_label, label, multi=True)

        for route_rules in route_rules:
            self._set(route_rules.command, route_rules.value, multi=True)

        return self._section

    def print_routes(self):
        """Print out defined routes."""

        self._set('routers-list', True, cast=bool)

        return self._section

    def set_error_page(self, status, html_fpath):
        """Add an error page (html) for managed 403, 404, 500 response.

        :param int status: HTTP status code.

        :param str|unicode html_fpath: HTML page file path.

        """
        statuses = [403, 404, 500]

        status = int(status)

        if status not in statuses:
            raise ConfigurationError(
                'Code `%s` for `routing.set_error_page()` is unsupported. Supported: %s' %
                (status, ', '.join(map(str, statuses))))

        self._set('error-page-%s' % status, html_fpath, multi=True)

        return self._section
