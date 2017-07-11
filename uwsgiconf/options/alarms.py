from operator import attrgetter

from ..base import OptionsGroup, ParametrizedValue
from ..utils import listify, filter_locals, make_key_val_string


class Alarm(ParametrizedValue):

    def __init__(self, alias, *args, **kwargs):
        self.alias = alias or ''
        super(Alarm, self).__init__(*args)


class AlarmCommand(Alarm):
    """Run a shell command, passing the log line to its stdin."""

    name = 'cmd'

    def __init__(self, alias, command):
        super(AlarmCommand, self).__init__(alias, command)


class AlarmSignal(Alarm):
    """Raise an uWSGI signal."""

    name = 'signal'

    def __init__(self, alias, sig_num):
        super(AlarmSignal, self).__init__(alias, sig_num)


class AlarmMule(Alarm):
    """Send the log line to a mule waiting for messages."""

    name = 'mule'

    def __init__(self, alias, mule_id):
        super(AlarmMule, self).__init__(alias, mule_id)


class AlarmCurl(Alarm):
    """Send the log line to a cURL-able URL."""

    name = 'curl'
    requires_plugin = 'alarm_curl'
    args_joiner = ';'

    def __init__(
            self, alias, url, method=None, ssl=None, ssl_insecure=None,
            auth_user=None, auth_pass=None,
            timeout=None, conn_timeout=None,
            mail_from=None, mail_to=None, subject=None):

        opts = make_key_val_string(
            filter_locals(locals(), drop=['alias', 'url']),
            bool_keys=['ssl', 'ssl_insecure'],
            items_separator=self.args_joiner,
        )
        super(AlarmCurl, self).__init__(alias, url, opts)


class AlarmXmpp(Alarm):
    """Send the log line via XMPP/jabber."""

    name = 'xmpp'
    requires_plugin = 'alarm_xmpp'
    args_joiner = ';'

    def __init__(self, alias, jid, password, recipients):
        super(AlarmXmpp, self).__init__(alias, jid, password, ','.join(listify(recipients)))


class Alarms(OptionsGroup):
    """Alarms.

    This subsystem allows the developer/sysadmin to "announce"
    special conditions of an app via various channels.

    * http://uwsgi-docs.readthedocs.io/en/latest/AlarmSubsystem.html

    """

    cls_alarm_command = AlarmCommand
    cls_alarm_signal = AlarmSignal
    cls_alarm_mule = AlarmMule
    cls_alarm_curl = AlarmCurl
    cls_alarm_xmpp = AlarmXmpp

    def __init__(self, *args, **kwargs):
        self._alarms = []
        super(Alarms, self).__init__(*args, **kwargs)

    def set_basic_params(self, msg_size=None, cheap=None, anti_loop_timeout=None):
        """
        :param int msg_size: Set the max size of an alarm message in bytes. Default: 8192.

        :param bool cheap: Use main alarm thread rather than create dedicated
            threads for curl-based alarms

        :param int anti_loop_timeout: Tune the anti-loop alarm system. Default: 3 seconds.

        """
        self._set('alarm-msg-size', msg_size)
        self._set('alarm-cheap', cheap, cast=bool)
        self._set('alarm-freq', anti_loop_timeout)

        return self._section

    def print_alarms(self):
        """Print out enabled alarms."""

        self._set('alarm-list', True, cast=bool)

        return self._section

    def register_alarm(self, alarm):
        """Register (create) an alarm.

        :param Alarm|list[Alarms] alarm: Alarm.

        """
        for alarm in listify(alarm):
            if alarm not in self._alarms:
                self._set('alarm', alarm, multi=True)
                self._alarms.append(alarm)

        return self._section

    def alarm_on_log(self, alarm, matcher, skip=False):
        """Raise (or skip) the specified alarm when a log line matches the specified regexp.

        :param Alarm|list[Alarms] alarm: Alarm.

        :param str|unicode matcher: Regular expression to match log line.

        :param bool skip:

        """
        self.register_alarm(alarm)

        value = '%s %s' % (
            ','.join(map(attrgetter('alias'), listify(alarm))),
            matcher)

        self._set('not-alarm-log' if skip else 'alarm-log', value)

        return self._section
