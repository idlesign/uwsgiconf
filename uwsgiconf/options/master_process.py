from ..base import OptionsGroup
from ..exceptions import ConfigurationError


class MasterProcess(OptionsGroup):
    """Master process is a separate process offering mentoring capabilities
    for other processes. Only one master process per uWSGI instance.

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
