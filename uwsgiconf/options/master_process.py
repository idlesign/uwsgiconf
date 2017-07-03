from ..base import OptionsGroup
from ..exceptions import ConfigurationError


class MasterProcess(OptionsGroup):
    """Master process is a separate process offering mentoring capabilities
    for other processes. Only one master process per uWSGI instance.

    uWSGI's built-in prefork+threading multi-worker management mode,
    activated by flicking the master switch on.
    For all practical serving deployments it's not really a good idea not to use master mode.

    """

    def set_basic_params(self, enabled=None, name=None, no_orphans=None, as_root=None,
                         subproc_check_interval=None):
        """

        :param bool enabled: Enable uWSGI master process

        :param str|unicode master_enabled: Set master process name to given value

        :param bool no_orphans: automatically kill workers if master dies (can be dangerous for availability)

        :param bool as_root: leave master process running as root

        :param int subproc_check_interval: set the interval (in seconds) of master checks. Default: 1
            The master process makes a scan of subprocesses, etc. every N seconds.
            You can increase this time if you need to, but it's DISCOURAGED.

        """
        self._set('master', enabled, cast=bool)
        self._set('procname-master', name)
        self._set('no-orphans', no_orphans)
        self._set('master-as-root', as_root)
        self._set('check-interval', subproc_check_interval)

        return self._section

    def add_cron_task(self, command, weekday=None, month=None, day=None, hour=None, minute=None,
                      legion=None, unique=None, harakiri=None):
        """Add a cron task running the given command on the given schedule.
        http://uwsgi.readthedocs.io/en/latest/Cron.html

        HINTS:
            * Use negative values to say `every`:
                hour=-3  stands for `every 3 hours`

            * Use - (minus) to make interval:
                minute='13-18'  stands for `from minute 13 to 18`

        NOTE: We use cron2 option available since 1.9.11.

        :param str|unicode command: Command to execute on schedule (with or without path).

        :param int|str|unicode weekday: Day of a the week number. Defaults to `each`.
            0 - Sunday  1 - Monday  2 - Tuesday  3 - Wednesday
            4 - Thursday  5 - Friday  6 - Saturday

        :param int|str|unicode month: Month number 1-12. Defaults to `each`.

        :param int|str|unicode day: Day of the month number 1-31. Defaults to `each`.

        :param int|str|unicode hour: Hour 0-23. Defaults to `each`.

        :param int|str|unicode minute: Minute 0-59. Defaults to `each`.

        :param str|unicode legion: Set legion (cluster) name to use this cron command against.
            Such commands are only executed by legion lord node.

        :param bool unique: Marks command as unique. Default to not unique.
            Some commands can take a long time to finish or just hang doing their thing.
            Sometimes this is okay, but there are also cases when running multiple instances
            of the same command can be dangerous.

        :param int harakiri: Enforce a time limit (in seconds) on executed commands.
            If a command is taking longer it will be killed.

        """
        rule = []
        locals_ = locals()

        for chunk in ['weekday', 'month', 'day', 'hour', 'minute', 'harakiri', 'legion']:
            val = locals_[chunk]
            if val is not None:
                rule.append('%s=%s' % (chunk, val))

        if unique:
            rule.append('unique=1')

        self._set('cron2', '%s %s' % (','.join(rule), command))

        return self._section

    def attach_process(self, process_or_pid_path, background):
        """Attach a command/daemon to the master process optionally managed by a pidfile.

        This will allow the uWSGI master to control/monitor/respawn this process.

        :param str|unicode process_or_pid_path:

        :param bool background: Must indicate whether process is in background.

        """
        if '/' in process_or_pid_path:  # todo check / - could't be in process name

            if background:
                # Attach a command/daemon to the master process managed by a pidfile (the command must daemonize)
                self._set('smart-attach-daemon', process_or_pid_path, multi=True)

            else:
                # Attach a command/daemon to the master process managed by a pidfile (the command must NOT daemonize)
                self._set('smart-attach-daemon2', process_or_pid_path, multi=True)

        else:
            if background:
                raise ConfigurationError('Background flag is only supported for pid-governed commands')

            # Attach a command/daemon to the master process (the command has to remain in foreground)
            self._set('attach-daemon', process_or_pid_path, multi=True)

        return self._section
