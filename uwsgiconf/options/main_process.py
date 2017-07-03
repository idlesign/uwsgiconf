from ..base import OptionsGroup


class MainProcess(OptionsGroup):
    """Main process is the uWSGi process."""

    def set_basic_params(self, touch_reload=None, priority=None, uid=None, gid=None, vacuum=None,
                 binary_path=None):
        """

        :param str|list touch_reload: Reload uWSGI if the specified file or directory is modified/touched.

        :param bool autonaming: Automatically set process name to something meaningful
            Generated process names may be 'uWSGI Master', 'uWSGI Worker #', etc.

        :param int priority: Set processes/threads priority (``nice``) value.

        :param str|unicode uid: Set uid to the specified username or uid.

        :param str|unicode gid: Set gid to the specified groupname or gid.

        :param bool vacuum: Try to remove all of the generated files/sockets
            (UNIX sockets and pidfiles) upon exit.

        :param str|unicode binary_path: Force uWSGI binary path.
            If you do not have uWSGI in the system path you can force its path with this option
            to permit the reloading system and the Emperor to easily find the binary to execute.

        """
        self._set('touch-reload', touch_reload, multi=True)
        self._set('prio', priority)
        self._set('uid', uid)
        self._set('gid', gid)
        self._set('vacuum', vacuum, cast=bool)
        self._set('binary-path', binary_path)

        return self._section

    def set_pid_file(self, fpath, before_privileges_drop=True):
        """Creates pidfile before or after privileges drop.

        :param str|unicode fpath: File path.
        :param bool before_privileges_drop:
        """
        self._set('pidfile' if before_privileges_drop else 'pidfile2', fpath)

        return self._section

    def set_naming_params(self, autonaming=None, prefix=None, postfix=None, name=None):
        """Setups processes naming parameters.

        :param bool autonaming: Automatically set process name to something meaningful.
            Generated process names may be 'uWSGI Master', 'uWSGI Worker #', etc.

        :param str prefix: Add prefix to process names.

        :param str postfix: Append string to process names.

        :param str name: Set process names to given static value.

        """
        self._set('auto-procname', autonaming, cast=bool)
        self._set('procname-prefix%s' % ('-spaced' if prefix and prefix.endswith(' ') else ''), prefix)
        self._set('procname-append', postfix)
        self._set('procname', name)

        return self._section
