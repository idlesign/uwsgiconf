from ..base import OptionsGroup


class MainProcess(OptionsGroup):
    """Main process is the uWSGi process."""

    class Events:
        """Events available for ``.run_command_on_event()`` method."""

        ASAP = 'asap'
        '''As soon as possible.'''

        JAIL_PRE = 'jail-pre'
        '''Before jailing.'''

        JAIL_IN = 'jail-in'
        '''In jail after initialization.'''

        JAIL_POST = 'jail-post'
        '''After jailing.'''

        PRIV_DROP_PRE = 'priv-drop-pre'
        '''Before privileges drop.'''

        PRIV_DROP_POST = 'priv-drop-post'
        '''Before privileges drop.'''

        EXIT = 'exit'
        '''Before app exit and reload.'''

        APP_LOAD_PRE = 'app-pre'
        '''Before app loading.'''

        APP_LOAD_POST = 'app-post'
        '''After app loading.'''

        VASSAL_START_IN = 'vassal-start-in'
        '''In vassal on start just before calling exec() directly in the new namespace.'''

        VASSAL_START_POST = 'vassal-start-post'
        '''In the emperor soon after a vassal has been spawn 
        setting 4 env vars, UWSGI_VASSAL_CONFIG, UWSGI_VASSAL_PID, 
        UWSGI_VASSAL_UID and UWSGI_VASSAL_GID.

        '''

    def set_basic_params(
            self, touch_reload=None, priority=None, vacuum=None, binary_path=None, honour_stdin=None):
        """

        :param str|list touch_reload: Reload uWSGI if the specified file or directory is modified/touched.

        :param int priority: Set processes/threads priority (``nice``) value.

        :param bool vacuum: Try to remove all of the generated files/sockets
            (UNIX sockets and pidfiles) upon exit.

        :param str|unicode binary_path: Force uWSGI binary path.
            If you do not have uWSGI in the system path you can force its path with this option
            to permit the reloading system and the Emperor to easily find the binary to execute.

        :param bool honour_stdin: do not remap stdin to /dev/null.
            By default, stdin is remapped to /dev/null on uWSGI startup.
            If you need a valid stdin (for debugging, piping and so on) use this option

        """
        self._set('touch-reload', touch_reload, multi=True)
        self._set('prio', priority)

        self._set('vacuum', vacuum, cast=bool)
        self._set('binary-path', binary_path)
        self._set('honour-stdin', honour_stdin, cast=bool)

        return self._section

    def set_owner_params(self, uid=None, gid=None, add_gids=None, set_immediate=False):
        """Set process owner params - user, group.

        :param str|unicode|int uid: Set uid to the specified username or uid.

        :param str|unicode|int gid: Set gid to the specified groupname or gid.

        :param list|str|unicode|int add_gids: Add the specified group id to the process credentials.
            This options allows you to add additional group ids to the current process.
            You can specify it multiple times.

        :param bool set_immediate: Setting them on top of your vassal file
            will force the instance to setuid()/setgid() as soon as possible
            and without the (theoretical) possibility to override them.

        """
        prefix = 'immediate-' if set_immediate else ''

        self._set(prefix + 'uid', uid)
        self._set(prefix + 'gid', gid)
        self._set('add-gid', add_gids, multi=True)

        return self._section

    def run_command_on_event(self, command, event=Events.ASAP):
        """Run the given command on a given event.

        :param str|unicode command:

        :param str|unicode event: See EVENT_* constants.

        """
        directive = {
            self.Events.ASAP: 'exec-asap',
            self.Events.JAIL_PRE: 'exec-pre-jail',
            self.Events.JAIL_IN: 'exec-in-jail',
            self.Events.JAIL_POST: 'exec-post-jail',
            self.Events.PRIV_DROP_PRE: 'exec-as-root',
            self.Events.PRIV_DROP_POST: 'exec-as-user',
            self.Events.EXIT: 'exec-as-user-atexit',
            self.Events.APP_LOAD_PRE: 'exec-pre-app',
            self.Events.APP_LOAD_POST: 'exec-post-app',
            self.Events.VASSAL_START_IN: 'exec-as-vassal',
            self.Events.VASSAL_START_POST: 'exec-as-emperor',
        }.get(event)

        self._set(directive, command, multi=True)

        return self._section

    def run_command_on_touch(self, command, target):
        """Run command when the specified file is modified/touched.

        :param str|unicode command:

        :param str|unicode target: File path.

        """
        self._set('touch-exec', '%s %s' % (target, command), multi=True)

        return self._section

    def set_pid_file(self, fpath, before_priv_drop=True, safe=False):
        """Creates pidfile before or after privileges drop.

        :param str|unicode fpath: File path.

        :param bool before_priv_drop:

        :param bool safe: The safe-pidfile works similar to pidfile
            but performs the write a little later in the loading process.
            This avoids overwriting the value when app loading fails,
            with the consequent loss of a valid PID number.

        """
        command = 'pidfile'

        if not before_priv_drop:
            command += '2'

        if safe:
            command = 'safe-' + command

        self._set(command, fpath)

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

    def set_reload_params(self, mercy=None, exit=None):
        """

        :param int mercy: Set the maximum time (in seconds) we wait
            for workers and other processes to die during reload/shutdown.

        :param bool exit: Force exit even if a reload is requested.

        """
        self._set('reload-mercy', mercy)
        self._set('exit-on-reload', exit)  # todo maybe move into separate exit-dedicated method

        return self._section
