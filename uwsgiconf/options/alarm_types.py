from ..base import ParametrizedValue
from ..utils import listify, filter_locals, KeyValue


class AlarmType(ParametrizedValue):

    def __init__(self, alias, *args, **kwargs):
        self.alias = alias or ''
        super(AlarmType, self).__init__(*args)


class AlarmCommand(AlarmType):
    """Run a shell command, passing info into its stdin."""

    name = 'cmd'

    def __init__(self, alias, command):
        super(AlarmCommand, self).__init__(alias, command)


class AlarmSignal(AlarmType):
    """Raise an uWSGI signal."""

    name = 'signal'

    def __init__(self, alias, sig_num):
        super(AlarmSignal, self).__init__(alias, sig_num)


class AlarmLog(AlarmType):
    """Print line into log."""

    name = 'log'

    def __init__(self, alias):
        super(AlarmLog, self).__init__(alias)


class AlarmMule(AlarmType):
    """Send info to a mule waiting for messages."""

    name = 'mule'

    def __init__(self, alias, mule_id):
        super(AlarmMule, self).__init__(alias, mule_id)


class AlarmCurl(AlarmType):
    """Send info to a cURL-able URL."""

    name = 'curl'
    plugin = 'alarm_curl'
    args_joiner = ';'

    def __init__(
            self, alias, url, method=None, ssl=None, ssl_insecure=None,
            auth_user=None, auth_pass=None,
            timeout=None, conn_timeout=None,
            mail_from=None, mail_to=None, subject=None):

        opts = KeyValue(
            filter_locals(locals(), drop=['alias', 'url']),
            bool_keys=['ssl', 'ssl_insecure'],
            items_separator=self.args_joiner,
        )
        super(AlarmCurl, self).__init__(alias, url, opts)


class AlarmXmpp(AlarmType):
    """Send info via XMPP/jabber."""

    name = 'xmpp'
    plugin = 'alarm_xmpp'
    args_joiner = ';'

    def __init__(self, alias, jid, password, recipients):
        super(AlarmXmpp, self).__init__(alias, jid, password, ','.join(listify(recipients)))
